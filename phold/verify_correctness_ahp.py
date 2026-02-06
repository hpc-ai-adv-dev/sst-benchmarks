#!/usr/bin/env python3
"""
Correctness tests comparing phold_dist_ahp.py to phold_dist.py.

Verifies that recvCount values match for each (i,j) component.
"""

import subprocess
import sys
import re
from typing import Dict, Tuple, List, Optional


def parse_recv_counts(output: str) -> Dict[Tuple[int, int], int]:
    """Parse recvCount values from simulation output.
    
    Output format: "X,Y:count" where X is row, Y is column.
    Returns dict mapping (row, col) -> count.
    """
    counts = {}
    # Match lines like "1,3:132" or "0,0:98"
    pattern = re.compile(r'^(\d+),(\d+):(\d+)$', re.MULTILINE)
    for match in pattern.finditer(output):
        row = int(match.group(1))
        col = int(match.group(2))
        count = int(match.group(3))
        counts[(row, col)] = count
    return counts


def run_simulation(script: str, height: int, width: int, num_rings: int,
                   num_nodes: int, num_ranks_per_node: int,
                   time_to_run: str = "1000ns",
                   extra_args: Optional[List[str]] = None) -> Tuple[str, int]:
    """Run a PHOLD simulation and return (output, exit_code).
    
    Uses srun with SST parallel-load=SINGLE.
    """
    total_ranks = num_nodes * num_ranks_per_node
    
    cmd = [
        "srun", "-N", str(num_nodes),
        "--ntasks-per-node", str(num_ranks_per_node),
        "sst", "--parallel-load=SINGLE",
        script,
        "--",
        f"--height={height}",
        f"--width={width}",
        f"--numRings={num_rings}",
        f"--timeToRun={time_to_run}",
        "--verbose=1",  # Enable recvCount output
    ]
    
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout for HPC queue wait
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT (30 min)", -1
    except Exception as e:
        return f"ERROR: {e}", -1


def compare_counts(og_counts: Dict[Tuple[int, int], int],
                   ahp_counts: Dict[Tuple[int, int], int]) -> Tuple[bool, str]:
    """Compare recvCount dictionaries.
    
    Returns (success, message).
    """
    og_keys = set(og_counts.keys())
    ahp_keys = set(ahp_counts.keys())
    
    # Check for missing/extra components
    missing_in_ahp = og_keys - ahp_keys
    extra_in_ahp = ahp_keys - og_keys
    
    if missing_in_ahp:
        return False, f"Components missing in AHP: {sorted(missing_in_ahp)}"
    
    if extra_in_ahp:
        return False, f"Extra components in AHP: {sorted(extra_in_ahp)}"
    
    # Compare counts
    mismatches = []
    for key in og_keys:
        if og_counts[key] != ahp_counts[key]:
            mismatches.append((key, og_counts[key], ahp_counts[key]))
    
    if mismatches:
        msg = "recvCount mismatches:\n"
        for (row, col), og_val, ahp_val in sorted(mismatches)[:10]:
            msg += f"  ({row},{col}): og={og_val}, ahp={ahp_val}\n"
        if len(mismatches) > 10:
            msg += f"  ... and {len(mismatches) - 10} more\n"
        return False, msg
    
    return True, f"All {len(og_keys)} components match"


def validate_config(height: int, num_rings: int, total_ranks: int) -> Tuple[bool, str]:
    """Check if configuration has enough rows per rank. Each rank needs at least
    num_rings rows.
    """
    rows_per_rank = height // total_ranks
    min_rows_needed = num_rings
    
    if rows_per_rank < min_rows_needed:
        return False, (
            f"Invalid config: {rows_per_rank} rows/rank < {min_rows_needed} "
            f"(numRings={num_rings})"
        )
    return True, "Config valid"


class TestCase:
    """A single test case configuration."""
    
    def __init__(self, name: str, height: int, width: int, num_rings: int,
                 num_nodes: int, num_ranks_per_node: int,
                 time_to_run: str = "1000ns"):
        self.name = name
        self.height = height
        self.width = width
        self.num_rings = num_rings
        self.num_nodes = num_nodes
        self.num_ranks_per_node = num_ranks_per_node
        self.time_to_run = time_to_run
        self.total_ranks = num_nodes * num_ranks_per_node
    
    def __str__(self):
        return (
            f"{self.name}: {self.height}x{self.width} grid, "
            f"numRings={self.num_rings}, "
            f"{self.num_nodes}N x {self.num_ranks_per_node}R = "
            f"{self.total_ranks} ranks"
        )


def run_test(test: TestCase, verbose: bool = True) -> Tuple[bool, str]:
    """Run a single test case."""
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running: {test}")
        print(f"{'='*60}")
    
    # Validate configuration
    valid, msg = validate_config(test.height, test.num_rings, test.total_ranks)
    if not valid:
        return False, f"SKIP: {msg}"
    
    # Run original implementation
    if verbose:
        print("Running phold_dist.py...")
    og_output, og_exit = run_simulation(
        "phold_dist.py",
        test.height, test.width, test.num_rings,
        test.num_nodes, test.num_ranks_per_node,
        test.time_to_run
    )
    
    if og_exit != 0:
        return False, f"Original failed with exit code {og_exit}:\n{og_output[:500]}"
    
    og_counts = parse_recv_counts(og_output)
    if not og_counts:
        return False, f"No recvCounts parsed from original output:\n{og_output[:500]}"
    
    if verbose:
        print(f"  Parsed {len(og_counts)} components from original")
    
    # Run AHP implementation
    if verbose:
        print("Running phold_dist_ahp.py...")
    ahp_output, ahp_exit = run_simulation(
        "phold_dist_ahp.py",
        test.height, test.width, test.num_rings,
        test.num_nodes, test.num_ranks_per_node,
        test.time_to_run
    )
    
    if ahp_exit != 0:
        return False, f"AHP failed with exit code {ahp_exit}:\n{ahp_output[:500]}"
    
    ahp_counts = parse_recv_counts(ahp_output)
    if not ahp_counts:
        return False, f"No recvCounts parsed from AHP output:\n{ahp_output[:500]}"
    
    if verbose:
        print(f"  Parsed {len(ahp_counts)} components from AHP")
    
    # Compare results
    success, msg = compare_counts(og_counts, ahp_counts)
    return success, msg


def print_counts_grid(counts: Dict[Tuple[int, int], int], height: int, width: int,
                      label: str) -> None:
    """Print recvCounts in a grid format for visual inspection."""
    print(f"\n{label} recvCounts ({height}x{width} grid):")
    print("-" * (width * 6 + 5))
    
    for row in range(height):
        row_vals = []
        for col in range(width):
            val = counts.get((row, col), -1)
            row_vals.append(f"{val:5d}")
        print(f"R{row:02d}: {' '.join(row_vals)}")
    print()


def run_inspect_single(height: int, width: int, num_rings: int,
                       num_nodes: int, num_ranks: int, label: str) -> int:
    """Run inspection for a single configuration and return 0 if match, 1 if diff."""
    total_ranks = num_nodes * num_ranks
    
    print(f"\n{'='*60}")
    print(f"INSPECT: {label}")
    print(f"  {height}x{width} grid, numRings={num_rings}")
    print(f"  {num_nodes} node(s) x {num_ranks} ranks = {total_ranks} total ranks")
    print(f"  Rows per rank: {height // total_ranks}")
    print(f"{'='*60}")
    
    # Validate
    valid, msg = validate_config(height, num_rings, total_ranks)
    if not valid:
        print(f"Invalid config: {msg}")
        return 1
    
    # Run original
    print("\nRunning phold_dist.py...")
    og_output, og_exit = run_simulation(
        "phold_dist.py", height, width, num_rings,
        num_nodes, num_ranks, "1000ns"
    )
    if og_exit != 0:
        print(f"Original failed: {og_output[:500]}")
        return 1
    og_counts = parse_recv_counts(og_output)
    print(f"  Parsed {len(og_counts)} components")
    
    # Run AHP
    print("Running phold_dist_ahp.py...")
    ahp_output, ahp_exit = run_simulation(
        "phold_dist_ahp.py", height, width, num_rings,
        num_nodes, num_ranks, "1000ns"
    )
    if ahp_exit != 0:
        print(f"AHP failed: {ahp_output[:500]}")
        return 1
    ahp_counts = parse_recv_counts(ahp_output)
    print(f"  Parsed {len(ahp_counts)} components")
    
    # Print grids side by side (or sequentially for readability)
    print_counts_grid(og_counts, height, width, "Original (phold_dist.py)")
    print_counts_grid(ahp_counts, height, width, "AHP (phold_dist_ahp.py)")
    
    # Show differences
    print("COMPARISON:")
    print("-" * 40)
    diffs = []
    for key in sorted(og_counts.keys()):
        og_val = og_counts.get(key, -1)
        ahp_val = ahp_counts.get(key, -1)
        if og_val != ahp_val:
            diffs.append((key, og_val, ahp_val))
    
    if diffs:
        print(f"Found {len(diffs)} differences:")
        for (row, col), og_val, ahp_val in diffs[:20]:
            diff = ahp_val - og_val
            print(f"  ({row},{col}): og={og_val}, ahp={ahp_val} (diff={diff:+d})")
        if len(diffs) > 20:
            print(f"  ... and {len(diffs) - 20} more")
    else:
        print("All values match! ✓")
    
    return 0 if not diffs else 1


def run_inspect_mode(tests: List['TestCase'], test_name: Optional[str]) -> int:
    """Run inspect mode - print detailed recvCount values for comparison.
    
    If no test specified, runs both base configurations (8x8 grid).
    """
    # If a specific test is given, run just that one
    if test_name:
        matching = [t for t in tests if t.name == test_name]
        if not matching:
            print(f"Test '{test_name}' not found")
            return 1
        test = matching[0]
        # For inspection, use a smaller grid
        height = min(test.height, 16)
        width = min(test.width, 16)
        return run_inspect_single(
            height, width, test.num_rings,
            test.num_nodes, test.num_ranks_per_node, test.name
        )
    
    # Default: run both base configurations
    print("Running inspection on both base configurations...")
    
    result1 = run_inspect_single(
        height=8, width=8, num_rings=2,
        num_nodes=1, num_ranks=2,
        label="base_8x8_1n_2r (1 node, 2 ranks)"
    )
    
    result2 = run_inspect_single(
        height=8, width=8, num_rings=2,
        num_nodes=2, num_ranks=2,
        label="base_8x8_2n_2r (2 nodes, 2 ranks each)"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("INSPECT SUMMARY:")
    print(f"  base_8x8_1n_2r: {'PASS ✓' if result1 == 0 else 'FAIL ✗'}")
    print(f"  base_8x8_2n_2r: {'PASS ✓' if result2 == 0 else 'FAIL ✗'}")
    print(f"{'='*60}")
    
    return 0 if (result1 == 0 and result2 == 0) else 1


def get_test_cases() -> List[TestCase]:
    """Define test cases.
    
    Each test ensures enough rows per rank for the given numRings.
    Rule: rows_per_rank >= 2 * numRings
    
    12 tests total:
    - 2 base case tests on 8x8 grid with ring size 2
    - 2 tests per ring size (1-5): one single-node multi-rank, one multi-node multi-rank
    """
    tests = []
    
    # ==========================================================================
    # Base case tests (8x8 grid, ring size 2)
    # ==========================================================================
    
    # 8x8 grid: 8/2=4 rows/rank, need 2*2=4, so 1N2R works
    tests.append(TestCase(
        name="base_8x8_1n_2r",
        height=8, width=8, num_rings=2,
        num_nodes=1, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    # 8x8 grid: 8/4=2 rows/rank, need 2*2=4, so need 2N2R (4 ranks total)
    # Actually 8/4=2 < 4, so we need fewer total ranks. 2N*2R=4 ranks => 8/4=2 rows/rank < 4
    # Let's use 2N1R for multinode: 8/2=4 rows/rank >= 4 ✓
    # But user wants 2Nx2R, so total=4 ranks, 8/4=2 rows < 4. Need bigger grid or fewer ranks.
    # For 2Nx2R (4 ranks): need height >= 4*4=16. Use 16x8 grid.
    tests.append(TestCase(
        name="base_8x8_2n_2r",
        height=8, width=8, num_rings=2,
        num_nodes=2, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    # ==========================================================================
    # Ring size 1 tests
    # ==========================================================================
    
    # Single node, 4 ranks: 64/4=16 rows/rank >= 2 ✓
    tests.append(TestCase(
        name="ring1_1n_4r",
        height=64, width=64, num_rings=1,
        num_nodes=1, num_ranks_per_node=4,
        time_to_run="1000ns"
    ))
    
    # Multi-node: 2 nodes, 2 ranks each (4 total): 64/4=16 rows/rank >= 2 ✓
    tests.append(TestCase(
        name="ring1_2n_2r",
        height=64, width=64, num_rings=1,
        num_nodes=2, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    # ==========================================================================
    # Ring size 2 tests
    # ==========================================================================
    
    # Single node, 4 ranks: 64/4=16 rows/rank >= 4 ✓
    tests.append(TestCase(
        name="ring2_1n_4r",
        height=64, width=64, num_rings=2,
        num_nodes=1, num_ranks_per_node=4,
        time_to_run="1000ns"
    ))
    
    # Multi-node: 2 nodes, 2 ranks each (4 total): 64/4=16 rows/rank >= 4 ✓
    tests.append(TestCase(
        name="ring2_2n_2r",
        height=64, width=64, num_rings=2,
        num_nodes=2, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    # ==========================================================================
    # Ring size 3 tests
    # ==========================================================================
    
    # Single node, 4 ranks: 64/4=16 rows/rank >= 6 ✓
    tests.append(TestCase(
        name="ring3_1n_4r",
        height=64, width=64, num_rings=3,
        num_nodes=1, num_ranks_per_node=4,
        time_to_run="1000ns"
    ))
    
    # Multi-node: 2 nodes, 2 ranks each (4 total): 64/4=16 rows/rank >= 6 ✓
    tests.append(TestCase(
        name="ring3_2n_2r",
        height=64, width=64, num_rings=3,
        num_nodes=2, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    # ==========================================================================
    # Ring size 4 tests
    # ==========================================================================
    
    # Single node, 4 ranks: 64/4=16 rows/rank >= 8 ✓
    tests.append(TestCase(
        name="ring4_1n_4r",
        height=64, width=64, num_rings=4,
        num_nodes=1, num_ranks_per_node=4,
        time_to_run="1000ns"
    ))
    
    # Multi-node: 2 nodes, 2 ranks each (4 total): 64/4=16 rows/rank >= 8 ✓
    tests.append(TestCase(
        name="ring4_2n_2r",
        height=64, width=64, num_rings=4,
        num_nodes=2, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    # ==========================================================================
    # Ring size 5 tests (need 2*5=10 rows/rank minimum)
    # ==========================================================================
    
    # Single node, 4 ranks: 64/4=16 rows/rank >= 10 ✓
    tests.append(TestCase(
        name="ring5_1n_4r",
        height=64, width=64, num_rings=5,
        num_nodes=1, num_ranks_per_node=4,
        time_to_run="1000ns"
    ))
    
    # Multi-node: 2 nodes, 2 ranks each (4 total): 64/4=16 rows/rank >= 10 ✓
    tests.append(TestCase(
        name="ring5_2n_2r",
        height=64, width=64, num_rings=5,
        num_nodes=2, num_ranks_per_node=2,
        time_to_run="1000ns"
    ))
    
    return tests


def main():
    """Run all correctness tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PHOLD correctness tests")
    parser.add_argument(
        "--test", type=str, default=None,
        help="Run only the specified test (by name)"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available tests and exit"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Only show pass/fail summary"
    )
    parser.add_argument(
        "--inspect", action="store_true",
        help="Print detailed recvCount values for eyeball comparison (uses smallest config)"
    )
    args = parser.parse_args()
    
    tests = get_test_cases()
    
    if args.list:
        print("Available tests:")
        for t in tests:
            valid, _ = validate_config(t.height, t.num_rings, t.total_ranks)
            status = "✓" if valid else "✗"
            print(f"  {status} {t}")
        return 0
    
    if args.inspect:
        return run_inspect_mode(tests, args.test)
    
    if args.test:
        tests = [t for t in tests if t.name == args.test]
        if not tests:
            print(f"Test '{args.test}' not found")
            return 1
    
    passed = 0
    failed = 0
    skipped = 0
    results = []
    
    for test in tests:
        success, msg = run_test(test, verbose=not args.quiet)
        
        if "SKIP" in msg:
            skipped += 1
            status = "SKIP"
        elif success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
        
        results.append((test.name, status, msg))
        
        if not args.quiet:
            print(f"\n{status}: {msg}")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    for name, status, msg in results:
        symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "○"}[status]
        print(f"  {symbol} {name}: {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
