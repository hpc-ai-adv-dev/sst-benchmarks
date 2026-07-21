import os
import sys
import unittest

THIS_DIR = os.path.dirname(__file__)
MERLIN_DIR = os.path.dirname(THIS_DIR)
if MERLIN_DIR not in sys.path:
    sys.path.insert(0, MERLIN_DIR)

from workflow_args import format_command_preview, generate_merlin_run_specs


class TestWorkflowArgs(unittest.TestCase):
    def test_deterministic_count(self):
        specs = generate_merlin_run_specs(
            node_counts=[1, 2],
            rank_counts=[1],
            topologies=["mesh"],
            mesh_params={"mesh_shape": ["2x2", "4x4"]},
            endpoint_params={"tg_packets_to_send": [10, 20]},
        )

        # 2 nodes * 1 rank * 2 mesh shapes * 2 packet counts
        self.assertEqual(len(specs), 8)

    def test_stochastic_reproducible(self):
        kwargs = dict(
            node_counts=[1, 4],
            rank_counts=[1, 2],
            topologies=["mesh", "dragonfly"],
            mesh_params={"mesh_shape": ["2x2", "4x4"]},
            dragonfly_params={"dragonfly_num_groups": [3, 8]},
            stochastic_samples=6,
            stochastic_seed=123,
        )
        specs_a = generate_merlin_run_specs(**kwargs)
        specs_b = generate_merlin_run_specs(**kwargs)

        self.assertEqual([spec.run_id for spec in specs_a], [spec.run_id for spec in specs_b])
        self.assertEqual([spec.config_args for spec in specs_a], [spec.config_args for spec in specs_b])

    def test_topology_specific_args_only(self):
        specs = generate_merlin_run_specs(
            topologies=["mesh", "dragonfly"],
            mesh_params={"mesh_shape": ["2x2"]},
            dragonfly_params={"dragonfly_num_groups": [5]},
        )

        mesh_spec = next(spec for spec in specs if spec.metadata["topology"] == "mesh")
        dragonfly_spec = next(spec for spec in specs if spec.metadata["topology"] == "dragonfly")

        mesh_tokens = " ".join(mesh_spec.config_args)
        self.assertIn("--mesh-shape", mesh_tokens)
        self.assertNotIn("--dragonfly-num-groups", mesh_tokens)

        dragonfly_tokens = " ".join(dragonfly_spec.config_args)
        self.assertIn("--dragonfly-num-groups", dragonfly_tokens)
        self.assertNotIn("--mesh-shape", dragonfly_tokens)

    def test_missing_seed_for_stochastic_raises(self):
        with self.assertRaises(ValueError):
            generate_merlin_run_specs(stochastic_samples=5)

    def test_command_preview_has_expected_sections(self):
        spec = generate_merlin_run_specs(topologies=["fattree"])[0]
        preview = format_command_preview(spec)

        self.assertIn("srun", preview)
        self.assertIn("mpirun", preview)
        self.assertIn("sst", preview["srun"])
        self.assertIn("merlin_benchmark.py", preview["mpirun"])


if __name__ == "__main__":
    unittest.main()
