# CI Experiment Layout

The CI workflow keeps experiment-specific assets under `.github/ci/experiments/<experiment>/`.
Each experiment folder owns:

- `test.sh` for the base simulation check.
- `checkpoint.sh` for the checkpoint-generation check.
- `restore.sh` for the checkpoint-restore check.
- One or more `.good` files used as the expected output for each SST version the experiment supports.

The workflow entrypoint is [ci.yaml](../workflows/ci.yaml). It selects an experiment from the matrix and runs the scripts in that experiment's CI folder.

## Run Locally

Use this flow when SST is already installed on your machine and available on `PATH`.

1. Build the experiment library.

```bash
cd pingpong
make clean && make
cd ..
```

2. Run the experiment test script from the repository root and pass the SST version tag you are using.

```bash
./.github/ci/experiments/pingpong/test.sh pingpong master
```

The second argument must match the version tag expected by the CI scripts. Current tags in [ci.yaml](../workflows/ci.yaml) are:

- `15.1.2`
- `16.0.0`
- `master`

If you want to reproduce the full CI flow locally, run the checkpoint and restore scripts the same way:

```bash
./.github/ci/experiments/pingpong/checkpoint.sh pingpong master
./.github/ci/experiments/pingpong/restore.sh pingpong master
```

## Run In A Devcontainer

To test against the SST build inside the devcontainer, the flow is exactly the same as above, just make sure you're running the scripts from inside the devcontainer shell.

1. Start the devcontainer and open a shell in the repository root.
2. Rebuild the experiment inside the container.

```bash
cd pingpong
make clean && make
cd ..
```

3. Run the test script from the repository root and pass the SST version tag built in the devcontainer.

```bash
./.github/ci/experiments/pingpong/test.sh pingpong master
```

4. Optionally run checkpoint and restore verification.

```bash
./.github/ci/experiments/pingpong/checkpoint.sh pingpong master
./.github/ci/experiments/pingpong/restore.sh pingpong master
```

## Add A New Experiment

1. Create the benchmark directory at the repository root and make sure `make` builds a shared library matching `lib*.so`.
2. Create a matching CI folder at `.github/ci/experiments/<experiment>/`.
3. Add `test.sh`, `checkpoint.sh`, and `restore.sh` to that folder.
4. Add the expected output `.good` files used by those scripts.
5. Make the scripts executable.
6. Add the experiment to the `matrix.experiment` list in [ci.yaml](../workflows/ci.yaml) with its `id` and repository-relative `path`.

The experiment scripts should follow the existing contract:

- Argument 1: repository-relative path to the experiment directory.
- Argument 2: SST version tag from the workflow matrix.
- Build output: the experiment directory must contain the `lib*.so` artifact that CI uploads and downloads between jobs.

Minimal checklist for a new experiment:

```text
.github/ci/experiments/<experiment>/
	test.sh
	checkpoint.sh
	restore.sh
	<expected-output>.good
```

After adding a new experiment, validate it the same way CI will run it:

```bash
cd <experiment>
make clean
make
cd ..

./.github/ci/experiments/<experiment>/test.sh <experiment> <sst-version-tag>
./.github/ci/experiments/<experiment>/checkpoint.sh <experiment> <sst-version-tag>
./.github/ci/experiments/<experiment>/restore.sh <experiment> <sst-version-tag>
```
