import os
import subprocess
import shlex
import stat
import time
import json

def run_cmd(cmd):
    if isinstance(cmd, str):
        args = shlex.split(cmd)
    else:
        args = list(cmd)
    print(f"> {cmd}")
    subprocess.run(args, check=True)

def cd(path):
    os.chdir(f'{path}')
    print(f"> cd {path}")

def get_convert_to_sif():
    if not os.path.exists('convert-to-sif.sh'):
        run_cmd(f"wget -O convert-to-sif.sh 'https://raw.githubusercontent.com/arezaii/arkouda-containers/refs/heads/main/scripts/convert-to-sif.sh'")
    os.chmod("convert-to-sif.sh", os.stat("convert-to-sif.sh").st_mode | stat.S_IXUSR)


def run_in_container(cmd, container, additional_apptainer_args=''):
    curDir = os.getcwd()
    args = shlex.split(f"apptainer exec --no-home --bind {curDir}:{curDir} --pwd {curDir} {additional_apptainer_args} {container} bash -lc")
    args.append(cmd)
    run_cmd(args)

def get_e4s_cl_profile(profile_name=None):
    """Parse `e4s-cl profile show` into a dict.

    With no profile_name, reports the *selected* profile -- which is the one
    `e4s-cl launch` will actually use.
    """
    cmd = 'e4s-cl profile show' + (f' {profile_name}' if profile_name else '')
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"'{cmd}' failed:\n{result.stdout}\n{result.stderr}")

    profile = {'name': None, 'image': None, 'backend': None,
               'libraries': {}, 'files': []}
    section = None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('Bound libraries:'):
            section = 'libraries'
            continue
        if stripped.startswith('Bound files:'):
            section = 'files'
            continue
        if ':' in stripped and not stripped.startswith('-'):
            key, _, value = stripped.partition(':')
            key, value = key.strip().lower(), value.strip()
            if key == 'profile name':
                profile['name'] = value
            elif key == 'container image':
                profile['image'] = None if value == 'None' else value
            elif key == 'container tech':
                profile['backend'] = value
            section = None
            continue
        if stripped.startswith('- ') and section:
            entry = stripped[2:].strip()
            if section == 'libraries':
                soname, _, path = entry.partition(' (')
                profile['libraries'][soname.strip()] = path.rstrip(')').strip()
            else:
                profile['files'].append(entry)
    return profile


def get_container_mpi_sonames(container, binary='sst'):
    """SONAMEs of the MPI libraries the container's SST binary actually needs.

    `bin/sst` is only a bootstrap shim with no MPI in its NEEDED list; the real
    MPI-linked executable is `libexec/sstsim.x`, so resolve that first.
    """
    probe = (
        f'B=$(command -v {binary}); '
        'R="$(dirname $(dirname $B))/libexec/sstsim.x"; '
        '[ -x "$R" ] || R="$B"; '
        'echo "REAL=$R"; ldd "$R"'
    )
    args = shlex.split(f'apptainer exec --no-home {container} bash -lc')
    args.append(probe)
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f'Could not inspect {binary} in {container}:\n{result.stderr}')

    real_binary, sonames = None, {}
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith('REAL='):
            real_binary = stripped[len('REAL='):]
        elif 'mpi' in stripped.lower() and '=>' in stripped:
            soname, _, target = stripped.partition('=>')
            sonames[soname.strip()] = target.strip().split(' (')[0]
    return real_binary, sonames


def check_mpi_binding(container, profile_name=None, strict=True):
    """Verify e4s-cl will inject a host MPI into `container` before launching.

    If the selected profile has no MPI library bound, e4s-cl performs no
    substitution and the container's own MPI falls back to singleton init --
    every task silently becomes rank 0 of a 1-rank job.
    """
    pmi_prefixes = ('libpmi', 'libpmix', 'libpals', 'libcray-pmi')
    problems, warnings = [], []

    profile = get_e4s_cl_profile(profile_name)
    real_binary, container_mpi = get_container_mpi_sonames(container)

    bound_mpi = {s: p for s, p in profile['libraries'].items() if 'mpi' in s.lower()}
    bound_pmi = {s: p for s, p in profile['libraries'].items()
                 if s.lower().startswith(pmi_prefixes)}

    print(f"e4s-cl profile : {profile['name']}")
    print(f"profile image  : {profile['image']}")
    print(f"container SST  : {real_binary}")
    print(f"container MPI  : {', '.join(container_mpi) or '(none)'}")
    print(f"bound host MPI : {', '.join(f'{s} -> {p}' for s, p in bound_mpi.items()) or '(none)'}")
    print(f"bound host PMI : {', '.join(sorted(bound_pmi)) or '(none)'}")

    if profile['image'] is None:
        problems.append('Selected profile has no container image set.')
    elif os.path.realpath(profile['image']) != os.path.realpath(container):
        problems.append(
            f"Selected profile image ({profile['image']}) is not the container "
            f"this workflow launches ({container})."
        )

    if not container_mpi:
        problems.append(
            f'{real_binary} is not linked against MPI; the container cannot run multi-rank.'
        )

    if not bound_mpi:
        problems.append(
            f"Profile '{profile['name']}' binds no host MPI library. e4s-cl will not "
            'substitute MPI, so every task will singleton-init as rank 0 of 1. '
            'Populate the profile with `e4s-cl init` against this container.'
        )
    elif container_mpi and not (set(bound_mpi) & set(container_mpi)):
        warnings.append(
            f"Bound host MPI SONAMEs {sorted(bound_mpi)} do not match the SONAMEs the "
            f"container needs {sorted(container_mpi)}; substitution relies on ABI "
            'compatibility -- confirm the achieved rank count on a small run.'
        )

    if not bound_pmi:
        warnings.append(
            'No PMI library bound. MPI may not be able to bootstrap through Slurm.'
        )

    for warning in warnings:
        print(f'WARNING: {warning}')
    if problems:
        message = 'e4s-cl MPI binding check failed:\n' + '\n'.join(f'  - {p}' for p in problems)
        if strict:
            raise RuntimeError(message)
        print(message)
        return False

    print('OK: e4s-cl will inject a host MPI into the container.')
    return True


def check_achieved_ranks(run_output_dir, expected_ranks):
    """Compare the rank count SST reported against what the launcher requested."""
    profiling_file = os.path.join(run_output_dir, 'profiling.json')
    if not os.path.exists(profiling_file):
        return None
    with open(profiling_file) as f:
        actual = int(json.load(f)['metadata']['ranks'])
    if actual != expected_ranks:
        print(f'RANK MISMATCH in {run_output_dir}: expected {expected_ranks}, SST ran with {actual}')
    return actual


def wait_for_jobs(job_name=None):
    wait = True
    check_cmd = 'squeue --me | wc -l' if job_name is None else f'squeue --name {job_name} | wc -l'
    while wait:
        #check queue length
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        queue_length = int(result.stdout.strip())
        if queue_length == 1: # there's always the header line
            wait = False
        else:
            print(f"Waiting for jobs to complete... Queue length: {queue_length - 1}")
            time.sleep(5)

