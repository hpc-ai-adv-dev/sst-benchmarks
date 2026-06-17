# Cyclical Component/Subcomponent Checkpoint Test

This example demonstrates that SST checkpoint/restart remains correct even when there are cyclical references between components and subcomponents. This functions as a simple proof of concept for the main concerns around making the Merlin element library checkpointable. 

## What this test demonstrates

The key property being tested is a bidirectional reference between a component and its subcomponents:

- `ParentComponent` holds pointers to two subcomponents (`leftChild`, `rightChild`).
- Each `basicSubComponent` holds a pointer back to its owning `ParentComponent`.

That creates a cycle in the object graph:

`ParentComponent -> basicSubComponent -> ParentComponent`

Both sides of this relationship are serialized, then restored from checkpoint.

## Files

- `Parent.h` / `Parent.cpp`
  - Defines `ParentComponent`.
  - Loads two anonymous subcomponents via `loadAnonymousSubComponent`.
  - Serializes parent-side state and child pointers in `serialize_order`.
- `Child.h` / `Child.cpp`
  - Defines the subcomponent API (`basicSubComponentAPI`) and implementation (`basicSubComponent`).
  - Subcomponent stores a back-pointer to `ParentComponent` and uses it in `handleEvent`.
  - Serializes subcomponent state including the parent pointer.
- `cyclical.py`
  - Builds a 10-component ring topology.
  - Uses deterministic random initialization (`random.seed(42)`) so runs are reproducible.

## Build

From this directory:

```bash
make
```

This produces `libcyclical.so` and registers the element library.

## Run: baseline with checkpoint creation

```bash
sst --checkpoint-sim-period=100ns --checkpoint-prefix=checkpoint cyclical.py > original_output.txt
```

This creates a checkpoint manifest at:

`checkpoint/checkpoint_1_100000/checkpoint_1_100000.sstcpt`

## Run: restart from checkpoint

```bash
sst checkpoint/checkpoint_1_100000/checkpoint_1_100000.sstcpt > restored_output.txt
```

SST auto-detects `.sstcpt` as restart input.

## How to validate correctness

A strict byte-for-byte diff is not the best check because:

- Parent pointer addresses naturally differ between processes/runs.
- Finalization print order may differ while representing the same final state.

Use semantic checks instead:

```bash
# Both runs should end at the same simulated time
grep "Simulation is complete" original_output.txt restored_output.txt

# Compare final component/subcomponent states independent of line order
grep -E "is finishing\. Final value|is finishing\. Final amount|Simulation is complete" original_output.txt | sort > /tmp/orig.summary
grep -E "is finishing\. Final value|is finishing\. Final amount|Simulation is complete" restored_output.txt | sort > /tmp/rest.summary
diff -u /tmp/orig.summary /tmp/rest.summary
```

Expected outcome:

- Both runs report `Simulation is complete, simulated time: 170 ns`.
- Final component values and subcomponent amounts match between baseline and restart.
