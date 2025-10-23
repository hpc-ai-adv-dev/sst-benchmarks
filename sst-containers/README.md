# SST in Containers

These are instructions for creating and using SST containers on a desktop
and an HPE EX system for the development of SST components for discrete event
simulations.

The document assumes you have an SST component library you are developing and
would like to use containers for this purpose.

The instructions are written with `podman` in mind, but the build and run
instructions should also work with `docker` by replacing the `podman` commands
with `docker` commands in most cases. For HPC systems,
we recommend and show how to use `apptainer` with `e4s-cl`.

The first section shows a complete working example of building and
running an SST container on a desktop.  The later sections provide
more details about each step.

## Overview

* Complete working example: Building and running SST 15.0.0 container on a desktop
* Installing/verifying required dependencies for this process
* Downloading the SST-core and other needed software sources
* Building the SST container
* Providing SST component C++ files and topology input files in Python
* Running a simulation on a desktop and HPE EX using SST container
* Troubleshooting

## Complete Working Example: Building and Running SST 15.0.0 Container on a Desktop/Laptop
Here's a complete example of building and using an SST container locally
with podman.  This example demonstrates the full workflow from container
building to running an SST simulation, which should be usable as a practical
foundation for SST development and testing.

This example demonstrates:
1. Building an SST container with version 15.0.0 and MPICH 4.0.2
2. Setting up the SST-benchmarks repository (game of life, 2D Pingpong, PHold)
3. Running a simulation inside the container
4. An optional next step of migrating the container to an HPE EX system.

More details about the process including setting up prerequisite software and
troubleshooting tips can be found in the later sections of this document.

### Prerequisites

Ensure you have the following:
- `podman` or `docker` installed and running
- Internet access for the initial build (to download sources)
- The `Containerfile` file available in your working directory
- The `download_tarballs.sh` script to fetch necessary source files
- This `sst-benchmarks` repository cloned to your local machine

### Step 0: Prepare the Environment
This step assumes access to the internet. Skip if the necessary source files
are already available locally.  Acquire the necessary source files by running
the `download_tarballs.sh` script:

```bash
# Download the required source files for SST and MPICH
./download_tarballs.sh 15.0.0 4.0.2
```

### Step 1: Build the SST Container

This step assumes access to the base OS image and OS package repositories and
the source files for SST and MPICH that were downloaded in the previous step.

Now, build the SST core container using the Containerfile:

```bash
# Build SST core container with specific versions
podman build \
  --build-arg SSTver=15.0.0 \
  --build-arg mpich=4.0.2 \
  -f Containerfile \
  -t sst-core:15.0.0 \
  .
```

This command:
- Uses SST version 15.0.0
- Uses MPICH version 4.0.2
- Builds only the core SST installation (no elements library)
- Tags the image as `sst-core:15.0.0`

**Note**: This build process will take 15-30 minutes depending on your system,
as it compiles MPICH and SST from source.

### Step 2: Set Up SST Benchmarks

Navigate to the `sst-benchmarks/pingpong` directory where `pingpong.py` lives. This step
assumes you have already cloned this repository and are currently working from
the directory where the `Containerfile` is located.

```bash
# Change to the benchmarks directory
cd ../pingpong
```

### Step 3: Run the SST Container

Launch the SST container with the benchmarks directory mounted:

```bash
# Run the SST container with current directory mounted
podman run -it --rm \
  --volume $(pwd):/workspace \
  --workdir /workspace \
  sst-core:15.0.0
```

This command:
- Runs the container interactively (`-it`)
- Removes the container when it exits (`--rm`)
- Mounts the current directory (`sst-benchmarks`) to `/workspace` inside the container
- Sets the working directory to `/workspace`
- Uses the `sst-core:15.0.0` image we just built

### Step 4: Build the SST Benchmarks (Inside Container)

Once inside the container, build the benchmark library:

```bash
# Inside the container - build the benchmarks
make
```

This compiles the C++ benchmark elements and makes them available to SST.

### Step 5: Run a Benchmark Simulation (Inside Container)

Run the pingpong benchmark with specific options:

```bash
# Inside the container - run the pingpong benchmark
sst pingpong.py -- --corners --verbose
```

This command:
- Runs the `pingpong.py` simulation script
- Uses the `--corners` option for corner case testing
- Uses the `--verbose` option for detailed output

### Expected Output

You should see output similar to:

```
Initial balls --
    0 east
    0 south
    9 west
    9 south
   90 east
   90 north
   99 west
   99 north
connect  pong_0 south -- pong_10 north
connect  pong_0 east -- pong_1 west
connect  pong_1 south -- pong_11 north
...
WARNING: Building component "sim" with no links assigned.
      50 s | vvvvvv pong_10
      50 s |  -----> pong_1
      50 s | ^^^^^^ pong_80
      50 s | pong_8 <-----
      50 s | ^^^^^^ pong_89
      50 s |  -----> pong_91
      50 s | pong_98 <-----
      50 s | vvvvvv pong_19
     100 s | ^^^^^^ pong_70
     100 s | pong_7 <-----
     100 s | ^^^^^^ pong_79
     100 s |  -----> pong_92
     ...
Simulation is complete, simulated time: 200 s
```

### Step 6: Exit the Container

When finished, exit the container:

```bash
# Inside the container - exit back to host
exit
```

### Optional: Migrate the Container to HPC Systems

After building the SST container on the desktop, you can migrate it to an HPC
system for further testing and development. This involves saving the container
as an OCI archive and then converting it to an Apptainer SIF file for use on
the HPC system.

Note that the architecture of the desktop and HPC system should be compatible
(e.g., both x86_64), otherwise you may need to adjust the build process to
target the HPC system's architecture.

Here is a working example of how to migrate the container from the example
above:

1. On the desktop, save the container as an OCI archive:

```bash
podman save --format oci-archive -o sst-core-15.0.0.tar sst-core:15.0.0
```

2. Transfer the `sst-core-15.0.0.tar` file to the HPC system using `scp` or
another file transfer method.

3. On the HPC system, convert the OCI archive to an Apptainer SIF file:

```bash
apptainer build sst-core-15.0.0.sif oci-archive://sst-core-15.0.0.tar
```

4. Now you can run the SST container on the HPC system using Apptainer:
```bash
apptainer run --bind $(pwd):/workspace --pwd /workspace sst-core-15.0.0.sif
```

Note: be sure to `exit` the running container before attempting to launch a distributed run in the next step.

5. To run a simulation on the HPC system, you can use `e4s-cl` to manage the execution
and binding of host libraries to the container:

```bash
e4s-cl -q launch srun -N 4 -- sst pingpong.py -- --corners --verbose
```


## Install/verify required dependencies for building and running SST containers

This section covers the system and software requirements for building and
running SST containers.

`podman` or `docker` needs to be installed and setup on a system where
you plan to build the container.

`apptainer` is recommended for running on HPC systems.

`e4s-cl` needs to be installed on a system where you would like
to run the SST container so as to leverage distributed parallelism.


### Quick Check if these are already on system

Use the following commands to check if all the required tools are installed.
```
  which podman
  which apptainer
  which e4s-cl
```
`podman` and `apptainer` may already be available on your system.

`e4s-cl` (https://e4s.io/e4s-cl.html) probably is not available.

See instructions for installing these dependencies on MacOS, Linux, and an HPE
EX system below.


### Linux Installation and Setup

Using `apt-get` as described below requires a connection to the internet.

See Apptainer installation instructions at https://apptainer.org/docs/user/main/quick_start.html#installation

(typically using your appropriate package manager to install, e.g.
`sudo apt-get install apptainer` or `sudo dnf install apptainer`)

See Podman installation instructions at https://podman.io/docs/installation#installing-on-linux

(typically using your appropriate package manager to install, e.g.
`sudo apt-get install podman` or `sudo dnf install podman podman-machine`)

Note that you or an administrator may need to add entries to the `/etc/subuid`
and `/etc/subgid` files.

### HPE EX Installation and setup

`podman` and `apptainer` are usually installed on an HPE EX system.
If they are not, you will probably want to ask your system support
team to install them.

Note that an administrator may need to add entries to the `/etc/subuid` and
`/etc/subgid` files per user for container tools to work properly without
root access.

For distributed parallelism to work properly inside the container, you will
need to install `e4s-cl` and setup a profile for your SST containers on the HPE
EX system.

Here are the instructions for installing `e4s-cl`:
https://e4s-cl.readthedocs.io/en/latest/installation.html.

### Mac Installation and Setup

We recommend building and running SST containers with `podman` on a mac.
Thus, these instructions only show how to install and setup `podman` on the mac.

Installing podman with homebrew.
(This step assumes a connection to the internet.)
```zsh
brew install podman
```

Alternatively see installation instructions at https://podman.io/docs/installation#macos

Create and start a virtual machine for podman.
```zsh
podman machine init
podman machine start
```
Running `podman machine init` above resulted in the following
internet accesses:
```
Looking up Podman Machine image at quay.io/podman/machine-os:5.5 to create VM
Getting image source signatures
Copying blob 1f5c0ec86103 done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
1f5c0ec861031a3e51ae30af3a34009ca344437609915ecf7833897e2292b448
Extracting compressed file: podman-machine-default-arm64.raw: done
Machine init complete
```

Check that the podman virtual machine is running
```zsh
podman info
```
**Memory Limitations**: Mac users may encounter build failures due to memory
constraints in the podman VM. If you see "Killed signal terminated program"
errors:

```bash
# Build with limited parallelism (safest)
podman build --build-arg NCPUS=1 -t sst-core:15.0.0 -f Containerfile .

# Or increase podman VM memory allocation
podman machine stop
podman machine rm
podman machine init --memory=4096  # 4GB RAM
podman machine start
```


### Verifying podman Installation

To verify that podman is properly installed and working, run the following commands:

1. Check the podman executable runs and reports its version:
```bash
podman --version
```

2. **Mac only**: Verify the virtual machine is running:
```bash
podman machine list
```
You should see output showing the machine status as "Running".

3. List available images:
```bash
podman images
```

4. Test basic functionality:
   - Mac/Linux with internet: Pull and run a simple container:
     ```bash
     podman run --rm hello-world
     ```
   - Local image: Run a locally available image by specifying its exact name and tag (as shown by `podman images`):
     ```bash
     podman run --rm my-image:latest echo "podman test successful"
     ```


### Verifying apptainer Installation

To verify that apptainer is properly installed and working, run the following
commands:

1. Check that apptainer runs and reports its version:
```bash
apptainer --version
```

2. Test basic functionality by running a simple container. This step assumes you have access to the docker.io repository and thus a connection to the internet.
```bash
apptainer run docker://hello-world
```
This should download and run a test container that prints a hello message.

3. Test building a simple container. This step assumes you have access to the docker.io repository.
```bash
apptainer build /tmp/test.sif docker://alpine:latest
```
This should build a simple container image file. You can then run it with:
```bash
apptainer run /tmp/test.sif
```

4. Exit the container:
```bash
exit
```

5. Clean up the test file:
```bash
rm /tmp/test.sif
```

### Verifying e4s-cl Installation

To verify that `e4s-cl` is properly installed and working, run the following
commands:

1. Check that `e4s-cl` runs and reports its version:
```bash
e4s-cl --version
```
2. Test that a profile has been setup:
```bash
e4s-cl profile list
```
3. View the details of your current profile:
```bash
e4s-cl profile show
```

## Downloading the SST-core and other needed software sources

All of the following need to be done on a system with internet
access and `wget` installed.

Use the `download_tarballs.sh` script to download the necessary source tarballs
for SST-core, SST-elements, and MPICH.

The default sst version is 15.0.0, and the default mpi version is 4.0.2.
Additionally, you can specify the version of each that you want. Here are some
examples:

```bash
# Download sources for SST version 15.0.0 and MPICH version 4.0.2
./download_tarballs.sh
# Download sources for an older SST version 14.1.0 and MPICH version 4.0.2
./download_tarballs.sh 14.1.0
# Download sources for SST version 15.0.0 and MPICH version 4.1.1
./download_tarballs.sh 15.0.0 4.1.1
```

SST-elements is always downloaded by the script, but can be included or excluded
in the SST container based on the selected container build target.

## Building SST Containers

Using `podman` to build SST containers allows for a flexible and portable
workflow.

This step assumes that podman can download Ubuntu base images from the
internet, and that the Ubuntu images can download and install packages.

### What should be in the directory before build

To build the SST container, you need to have the following files in your
working directory:

```bash
# Example tree view
tree .
.
├── Containerfile
├── mpich-4.0.2.tar.gz
├── sstcore-15.0.0.tar.gz
├── sstelements-15.0.0.tar.gz
```

Note that the version numbers in the tar.gz files may vary based on the
versions you downloaded.

### Example commands to build the SST container

Here is an example command to build the SST container using `podman`:

```bash
podman build -t sst:15.0.0 .
```

This command will build the SST container, without the elements library, using
the `Containerfile` in the current directory and tag it as `sst:15.0.0`.

As the following examples show, the supplied `Containerfile` accepts arguments
for SST version and MPICH version, allowing you to specify which versions to
build.

### Example command to build with specific versions

You can specify the SST and MPICH versions when building the container:

```bash
podman build \
  --build-arg SSTver=15.0.0 \
  --build-arg mpich=4.0.2 \
  -t sst:15.0.0 .
```
This command builds the SST container with SST version 15.0.0 and MPICH version
4.0.2, tagging it as `sst:15.0.0`.

You can also build the container with the SST-elements library by using the
`--target` option:

```bash
podman build \
  --build-arg SSTver=15.0.0 \
  --build-arg mpich=4.0.2 \
  --target sst-full \
  -t sst-full:15.0.0 .
```
This command builds the SST container with the elements library, tagging it as
`sst-full:15.0.0`.


### Creating Portable, OCI-Compatible Archives with podman save

This step allows you to create portable archives of your SST container images
that were created with podman. The archives can then be migrated to other
machines, or be used with apptainer or other container runtimes.
Here “portable” means it can be moved to another machine and imported into
podman or directly into apptainer. There are other options for formatting the
save output from podman, including docker, which is somewhat less portable than
the OCI-archive version because it did not import smoothly directly into
apptainer.

Note: This is an area where docker and podman commands differ. There is no
direct equivalent of `podman save` in docker that can output an OCI compatible
archive, but there are alternative steps one can take with docker to create
such an image that are outside the scope of this document.

```bash
# Save a container image as an OCI-compatible tar archive named image-name.tar
podman save --format oci-archive -o image-name.tar image:tag

# Examples:
# Save a base OS image (this example assumes connectivity to the docker.io repository)
podman save --format oci-archive -o ubuntu-jammy.tar docker.io/ubuntu:jammy

# Save a built SST container (this example assumes a local image named sst:latest)
podman save --format oci-archive -o sst-container.tar localhost/sst:latest
```

Note that these commands all use the `--format oci-archive` flag, which is
important for building the archive into an Apptainer SIF file later.

### Verifying Archives

After creating archives, verify they contain the expected images:

```bash
# List contents of an archive
tar -tf sst-container.tar | head -10

# Check archive size
ls -lh *.tar

# Test loading the archive (non-destructive)
podman load --input sst-container.tar
podman images | grep sst-container
```

### Loading Archives that were previously saved

To load a previously saved archive back into podman, use the `load` command:

```bash
# Load an OCI-archive
podman load -i sst-container.tar

# Verify the image was loaded successfully
podman images

# Test the loaded image
podman run --rm sst-container:latest echo "Image loaded successfully"
```

**Important Notes:**
- Use `--format oci-archive` for maximum compatibility
- Archives can be large; consider compression for transfer
- Keep track of image tags and versions in your archives

### Converting OCI Archives to Apptainer SIF Files

After creating OCI-compatible archives with `podman save`, you can convert them
to Apptainer's native SIF format for use on HPC systems.

#### Building SIF Files from OCI Archives

Use `apptainer build` to convert OCI archives to SIF format:

```bash
# Convert an OCI archive to SIF format
apptainer build output.sif oci-archive://path/to/archive.tar

# Examples:
# Convert the base image archive
apptainer build ubuntu-jammy.sif oci-archive://ubuntu-jammy.tar

# Convert an SST container archive
apptainer build sst-container.sif oci-archive://sst-container.tar

# Build with a specific name and location
apptainer build /path/to/containers/sst.sif oci-archive://sst-container.tar
```

#### Verifying SIF Files

After building SIF files, verify they work correctly:

```bash
# Check SIF file information
apptainer inspect sst.sif

# Test running the SIF file
apptainer run sst.sif

# Execute a command in the SIF file
apptainer exec sst.sif echo "SIF file is working"

# Check SIF file size
ls -lh *.sif
```

**Benefits of SIF Format:**
- Single-file container images (easier to manage)
- Optimized for HPC environments
- Better performance on shared filesystems

## Providing SST component C++ files and topology input files in Python

How to use your custom SST component library and specify the topology input
files in Python.

You will need to provide a Python script to launch your simulation.

See https://sst-simulator.org/sst-docs/docs/guides/runningSST.

For some examples, see the gameoflife and pingpong benchmarks in the
sst-benchmarks repository: https://github.com/brandon-neth/sst-benchmarks.

In the complete example at the beginning of this document, we show:
 1. entering the container to build the pingpong component library
 2. running the simulation using the Python script
 3. example output from the simulation

## Running SST Containers

### Running SST Container on Desktop/Laptop

This section covers how to run an SST container on a desktop or laptop using
`podman`.

It assumes you have an SST component library you are developing and testing with
SST.

If you do not have a component library, you can use the pingpong benchmark
from the `sst-benchmarks` repository, https://github.com/brandon-neth/sst-benchmarks.

If using the pingpong benchmark, set your working directory to the `pingpong/` directory.
Otherwise, set your working directory to where you build your SST component library.

**Important**: Ensure you are in the actual directory path, not an aliased or symbolic link path. On Linux systems, you can verify this with:

```bash
cd $(pwd -P)
```

This command resolves any symbolic links and ensures you're in the canonical path.

From your working directory, you can run the following command to launch the SST
container:

```bash
podman run -it -v $(pwd):/workspace --rm sst:latest
```

This will drop you into a shell inside the SST container with your current
working directory mounted at `/workspace`.

From here you will find sst added to the PATH so you can now build and run your
SST simulations.

Example using the sst-benchmarks repository:

```bash
podman run -it -v $(pwd):/workspace --rm sst:latest
# Inside the container, build the benchmarks
make
# Run a benchmark simulation
sst pingpong.py -- --corners
```

### Running SST Container on HPE EX
This section covers how to run an SST container on an HPE EX system using
`apptainer`.

It assumes you have the SST container built and stored in a podman OCI archive.

```bash
# Convert OCI archive to SIF format
apptainer build sst-15.0.0.sif oci-archive://sst-15.0.0.tar

# Run with apptainer
cd sst-benchmarks/pingpong
apptainer run --bind $(pwd):/workspace --pwd /workspace sst-15.0.0.sif

# Inside the container, run the same commands:
make
sst pingpong.py -- --corners --verbose
```

**Note**: By default, apptainer binds your HOME directory into the container. If this is not desirable, disable this behavior with the `--no-home` flag:

```bash
apptainer run --no-home --bind $(pwd):/workspace --pwd /workspace sst-15.0.0.sif
```

**Common Issue**: If you encounter an error when trying to `make` your project while running an SST container with apptainer, such as:

```
Unable to open configuration at either: /opt/SST/15.0.0/etc/sst/sstsimulator.conf or /home/users/<USER>/.sst/sstsimulator.conf, one of these files must be editable.
```

This can be resolved by creating an empty SST configuration file and binding it into the container:

```bash
# Create the SST configuration directory and file
mkdir -p ~/.sst
touch ~/.sst/sstsimulator.conf

# Run apptainer with the additional bind mount
apptainer run --bind $(pwd):/workspace --bind ~/.sst:/home/users/$USER/.sst --pwd /workspace sst-15.0.0.sif
```

#### Distributed Parallelism with e4s-cl and SST Containers

To run SST containers with distributed parallelism on an HPE EX system, you can
use `e4s-cl` to manage the container execution.

The purpose of this is to bind the host's shared libraries (like MPI, OFI, etc.)
into the container at runtime, which is necessary for HPC use of containers.

##### Running with e4s-cl

To schedule a job using slurm and e4s-cl, configure a submission script for
sbatch.  The following can be saved as `sst-submit.slurm` and used used in
this example:

```bash
#!/bin/bash

#SBATCH -t 02:25:00
#SBATCH -N 4
#SBATCH -o output.o%j

echo "slurm job id:" $SLURM_JOB_ID
e4s-cl -q launch srun -N 4 -- sst --print-timing-info=true pingpong.py -- --corners --verbose
```

Let's dissect the e4s-cl command. First, the `-q` flag specifies that e4s-cl
should run quietly. Without this you'll get information from e4s-cl about the
profile it used when running.

Next is the `launch` command which you can read more about here: https://e4s-cl.readthedocs.io/en/latest/reference/launch.html#

We specify `srun` as our launcher and give it the number of nodes with `-N 4`.
Following that is a double dash `--` that tells `e4s-cl` that we're done
entering launcher commands and the following arguments should be passed to the
running container.

`sst` was added to the `PATH` inside the container when it was built, so we can
call it directly with any expected flags (`--print-timing-info=true` in this
case) and our SDL file, `pingpong.py`. The custom SDL file uses the double dash
`--` immediately following it  to indicate we are done with the arguments to
`sst` and the following arguments are all for `pingpong.py`. See `pingpong.py
--help` for more information on the available arguments.

Save the submission script, I used `sst-submit.slurm` as a filename, so the
command to launch the job is just:
```bash
sbatch sst-submit.slurm
```

Your job should immediately get a job ID and you should be able to use the
`squeue` command to view the job scheduler queue and see the status of your job.

When the job is finished, the output will be in the file `output.o<jobID>`


## Troubleshooting

**If the build fails:**
- Ensure you have internet connectivity
- Check that podman is running: `podman info`
- Try building the base stage first: `podman build --target build-base -t test-base .`
- Try limiting the build to a lower number of parallel jobs by specifying the `NCPUS` build argument, e.g.:
  ```bash
  podman build --build-arg NCPUS=2 -t sst-core:latest .
  ```

**If the simulation fails:**
- Verify the benchmarks built successfully: `ls *.so`
- Check SST installation: `sst --version`
- Ensure you're in the correct directory inside the container: `pwd`
- Make sure the container image is on a file system available to all the compute nodes

**If you encounter "chdir: no such file or directory" errors:**
- Verify you have established a bind mount from the host to the container at a level that includes your simulation files
- Ensure you're not launching the container from an aliased or symbolic link path
- On Linux, use `cd $(pwd -P)` to resolve to the canonical path before running the container
- Check that your bind mount path is correct: `--bind $(pwd):/workspace`

**If you encounter SST configuration file errors on HPC systems:**
- The error typically looks like: "Unable to open configuration at either: /opt/SST/15.0.0/etc/sst/sstsimulator.conf or /home/users/<USER>/.sst/sstsimulator.conf"
- Create an empty SST configuration file: `mkdir -p ~/.sst && touch ~/.sst/sstsimulator.conf`
- Add a bind mount for the configuration directory when running apptainer: `--bind ~/.sst:/home/users/$USER/.sst`

**If HOME directory binding causes issues with apptainer:**
- Use the `--no-home` flag to disable automatic HOME directory binding: `apptainer run --no-home --bind $(pwd):/workspace ...`
- This prevents potential conflicts with host environment configurations