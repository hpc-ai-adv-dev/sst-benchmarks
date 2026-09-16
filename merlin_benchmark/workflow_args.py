"""Notebook-friendly argument builders for the Merlin benchmark.

This module mirrors the PHOLD workflow pattern but returns structured token lists
instead of pre-joined command strings.

Time-valued workflow parameters are interpreted as nanoseconds when provided as
numeric values or numeric strings without units. Those values are normalized to
strings ending with "ns" in generated MerlinRunSpec objects.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Any, Sequence


TOPOLOGY_VALUES = ("mesh", "dragonfly", "fattree")

TIME_PARAM_KEYS = frozenset(
    {
       "stop_at"
    }
)

DEFAULT_GLOBAL_PARAMS: dict[str, Any] = {
    "stop_at": "10us",
    "verbose": None,
}

DEFAULT_NETWORK_PARAMS: dict[str, Any] = {
    "flit_size_bytes": 8,
    "link_bw_gbps": 4,
    "link_lat_ns": 1,
    "xbar_bw_gbps": 4,
}

DEFAULT_ENDPOINT_PARAMS: dict[str, Any] = {
    "tg_output_file_name": "",
    "tg_input_latency": "20ns",
    "tg_output_latency": "20ns",
    "tg_input_buf_size": "4kB",
    "tg_output_buf_size": "4kB",
    "tg_num_vns": None,
    "tg_buffer_length": None,
    "tg_packets_to_send": None,
    "tg_packet_size": None,
    "tg_delay_between_packets": None,
    "tg_message_rate": None,
    "tg_packet_dest_pattern": None,
    "tg_packet_dest_seed": None,
    "tg_packet_dest_range_min": None,
    "tg_packet_dest_range_max": None,
    "tg_packet_dest_nearest_neighbor_size": None,
    "tg_packet_dest_hotspot_target": None,
    "tg_packet_dest_hotspot_target_probability": None,
    "tg_packet_dest_normal_mean": None,
    "tg_packet_dest_normal_sigma": None,
    "tg_packet_dest_binomial_mean": None,
    "tg_packet_dest_binomial_sigma": None,
    "tg_packet_dest_exponential_lambda": None,
    "tg_packet_size_pattern": None,
    "tg_packet_size_seed": None,
    "tg_packet_size_range_min": None,
    "tg_packet_size_range_max": None,
    "tg_packet_size_hotspot_target": None,
    "tg_packet_size_hotspot_target_probability": None,
    "tg_packet_size_normal_mean": None,
    "tg_packet_size_normal_sigma": None,
    "tg_packet_size_binomial_mean": None,
    "tg_packet_size_binomial_sigma": None,
    "tg_packet_size_exponential_lambda": None,
    "tg_packet_delay_pattern": None,
    "tg_packet_delay_seed": None,
    "tg_packet_delay_range_min": None,
    "tg_packet_delay_range_max": None,
    "tg_packet_delay_hotspot_target": None,
    "tg_packet_delay_hotspot_target_probability": None,
    "tg_packet_delay_normal_mean": None,
    "tg_packet_delay_normal_sigma": None,
    "tg_packet_delay_binomial_mean": None,
    "tg_packet_delay_binomial_sigma": None,
    "tg_packet_delay_exponential_lambda": None,
}

DEFAULT_MESH_PARAMS: dict[str, Any] = {
    "mesh_shape": "4x4",
    "mesh_width": "2x2",
    "mesh_local_ports": 2,
}

DEFAULT_DRAGONFLY_PARAMS: dict[str, Any] = {
    "dragonfly_hosts_per_router": 2,
    "dragonfly_routers_per_group": 4,
    "dragonfly_intergroup_links": 1,
    "dragonfly_num_groups": 9,
    "dragonfly_algorithm": "minimal",
    "dragonfly_adaptive_threshold": 2.0,
    "dragonfly_global_routing_mode": "absolute",
}

DEFAULT_FATTREE_PARAMS: dict[str, Any] = {
    "fattree_shape": "4,4:4,4:8",
}

TOPOLOGY_PARAM_DEFAULTS: dict[str, dict[str, Any]] = {
    "mesh": DEFAULT_MESH_PARAMS,
    "dragonfly": DEFAULT_DRAGONFLY_PARAMS,
    "fattree": DEFAULT_FATTREE_PARAMS,
}


@dataclass(frozen=True)
class MerlinRunSpec:
    """Argument payload for one benchmark run.

    Fields:
        run_id:
            Short stable identifier derived from run parameters.
        run_name:
            Human-readable run name including experiment, topology, execution
            shape, and run_id.
        launcher:
            Mapping with two entries:
            - "srun": token list for srun launcher arguments.
            - "mpirun": token list for mpirun launcher arguments.
        sst_args:
            Token list passed directly to the sst command.
        config_args:
            Token list passed to merlin_benchmark.py after "--".
        metadata:
            Provenance payload with experiment info, execution shape, and
            fully-resolved parameter values.
    """

    run_id: str
    run_name: str
    launcher: dict[str, list[str]]
    sst_args: list[str]
    config_args: list[str]
    metadata: dict[str, Any]

   

    def to_dict(self, *, config_script: str = "merlin_benchmark.py") -> dict[str, Any]:
        """Return a compact dict with command previews and top-level parameters.

        The command previews are stored as full shell strings, and the resolved
        run parameters are lifted out of metadata.parameters so callers can work
        with keys like ``dragonfly_adaptive_threshold`` directly.
        """

        preview = format_command_preview(self, config_script=config_script)
        summary = {
            "run_id": self.run_id,
            "run_name": self.run_name,
            "experiment_name": self.metadata["experiment_name"],
            "topology": self.metadata["topology"],
            "node_count": self.metadata["execution"]["node_count"],
            "rank_count": self.metadata["execution"]["rank_count"],
            "srun_command": preview["srun"],
            "mpirun_command": preview["mpirun"],
        }
        summary.update(self.metadata.get("parameters", {}))
        return summary


def generate_merlin_run_specs(
    *,
    node_counts: Sequence[int] = (1,),
    rank_counts: Sequence[int] = (1,),
    topologies: Sequence[str] = ("mesh",),
    global_params: dict[str, Any] | None = None,
    network_params: dict[str, Any] | None = None,
    endpoint_params: dict[str, Any] | None = None,
    mesh_params: dict[str, Any] | None = None,
    dragonfly_params: dict[str, Any] | None = None,
    fattree_params: dict[str, Any] | None = None,
    sst_extra_args: Sequence[str] = (),
    experiment_name: str = "merlin",
    stochastic_samples: int | None = None,
    stochastic_seed: int | None = None,
) -> list[MerlinRunSpec]:
    """Generate run specifications for notebook-driven Merlin workflows.

    Allowed arguments:
        node_counts:
            Non-empty sequence of positive integers.
        rank_counts:
            Non-empty sequence of positive integers.
        topologies:
            Non-empty sequence containing only "mesh", "dragonfly", and/or
            "fattree".
        global_params:
            Optional overrides for keys in DEFAULT_GLOBAL_PARAMS only.
        network_params:
            Optional overrides for keys in DEFAULT_NETWORK_PARAMS only.
        endpoint_params:
            Optional overrides for keys in DEFAULT_ENDPOINT_PARAMS only.
        mesh_params:
            Optional overrides for keys in DEFAULT_MESH_PARAMS only.
        dragonfly_params:
            Optional overrides for keys in DEFAULT_DRAGONFLY_PARAMS only.
        fattree_params:
            Optional overrides for keys in DEFAULT_FATTREE_PARAMS only.
        sst_extra_args:
                Extra tokens appended to sst_args. Any provided --timing-info
                options are ignored because --timing-info=3 is always enforced.
        experiment_name:
            Prefix used in generated run_name values.
        stochastic_samples:
            If None, deterministic Cartesian product mode is used.
            If set, must be > 0.
        stochastic_seed:
            Required when stochastic_samples is set.

    Deterministic mode:
        Each parameter value may be a scalar or a sequence of options.

    Time parameter normalization:
        Time-valued keys listed in TIME_PARAM_KEYS assume input values are in
        nanoseconds. Numeric values (or numeric strings without a unit suffix)
        are normalized to strings ending in "ns" in the returned
        MerlinRunSpec config_args and metadata parameters.

    Stochastic mode:
        Sampling is repeated stochastic_samples times.
        For any sequence value:
        - Two numeric values are treated as [min, max] range bounds.
        - Other sequences are treated as categorical choices.

    Not allowed:
        - Empty node_counts, rank_counts, or topologies.
        - Unknown topology names.
        - Unknown override keys in any *_params dictionary.
        - stochastic_samples <= 0.
        - Providing stochastic_samples without stochastic_seed.
        - Passing thread_counts (this API intentionally does not support thread
          count control).

    Returns:
        List of MerlinRunSpec objects, one per generated run.

    Raises:
        ValueError for validation failures listed above.
        TypeError if unsupported function keywords are passed.
    """

    _validate_topologies(topologies)
    _validate_positive_int_list("node_counts", node_counts)
    _validate_positive_int_list("rank_counts", rank_counts)

    global_space = _with_defaults(DEFAULT_GLOBAL_PARAMS, global_params)
    network_space = _with_defaults(DEFAULT_NETWORK_PARAMS, network_params)
    endpoint_space = _with_defaults(DEFAULT_ENDPOINT_PARAMS, endpoint_params)

    topology_spaces = {
        "mesh": _with_defaults(DEFAULT_MESH_PARAMS, mesh_params),
        "dragonfly": _with_defaults(DEFAULT_DRAGONFLY_PARAMS, dragonfly_params),
        "fattree": _with_defaults(DEFAULT_FATTREE_PARAMS, fattree_params),
    }

    if stochastic_samples is None:
        params = _deterministic_parameter_points(
            node_counts=node_counts,
            rank_counts=rank_counts,
            topologies=topologies,
            global_space=global_space,
            network_space=network_space,
            endpoint_space=endpoint_space,
            topology_spaces=topology_spaces,
        )
    else:
        if stochastic_samples <= 0:
            raise ValueError("stochastic_samples must be > 0")
        if stochastic_seed is None:
            raise ValueError("stochastic_seed is required when stochastic_samples is set")
        rng = random.Random(stochastic_seed)
        params = _stochastic_parameter_points(
            stochastic_samples=stochastic_samples,
            rng=rng,
            node_counts=node_counts,
            rank_counts=rank_counts,
            topologies=topologies,
            global_space=global_space,
            network_space=network_space,
            endpoint_space=endpoint_space,
            topology_spaces=topology_spaces,
        )

    return [
        _build_run_spec(
            run_parameters=run_parameters,
            experiment_name=experiment_name,
            sst_extra_args=list(sst_extra_args),
        )
        for run_parameters in params
    ]


def format_command_preview(
    run_spec: MerlinRunSpec,
    *,
    config_script: str = "merlin_benchmark.py",
) -> dict[str, str]:
    """Render shell-preview command strings from a run spec.

    Allowed arguments:
        run_spec:
            A MerlinRunSpec returned by generate_merlin_run_specs.
        config_script:
            Name or path of the benchmark configuration script to execute.

    Not allowed:
        - A run_spec that does not include launcher entries for both "srun"
          and "mpirun".
        - Non-string config_script values.

    Returns:
        Dictionary with two keys:
        - "srun": full command preview using srun launcher tokens.
        - "mpirun": full command preview using mpirun launcher tokens.
    """

    srun_cmd = " ".join(
        [
            "srun",
            *run_spec.launcher["srun"],
            "sst",
            *run_spec.sst_args,
            config_script,
            "--",
            *run_spec.config_args,
        ]
    )
    mpirun_cmd = " ".join(
        [
            "mpirun",
            *run_spec.launcher["mpirun"],
            "sst",
            *run_spec.sst_args,
            config_script,
            "--",
            *run_spec.config_args,
        ]
    )
    return {
        "srun": srun_cmd,
        "mpirun": mpirun_cmd,
    }


def _deterministic_parameter_points(
    *,
    node_counts: Sequence[int],
    rank_counts: Sequence[int],
    topologies: Sequence[str],
    global_space: dict[str, Any],
    network_space: dict[str, Any],
    endpoint_space: dict[str, Any],
    topology_spaces: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []

    shared_space = {
        "node_count": node_counts,
        "rank_count": rank_counts,
        **global_space,
        **network_space,
        **endpoint_space,
    }

    shared_points = _cartesian_product_dict(shared_space)

    for topology in topologies:
        topology_points = _cartesian_product_dict(topology_spaces[topology])
        for shared in shared_points:
            for topo_point in topology_points:
                points.append(
                    {
                        **shared,
                        "topology": topology,
                        "topology_params": topo_point,
                    }
                )

    return points


def _stochastic_parameter_points(
    *,
    stochastic_samples: int,
    rng: random.Random,
    node_counts: Sequence[int],
    rank_counts: Sequence[int],
    topologies: Sequence[str],
    global_space: dict[str, Any],
    network_space: dict[str, Any],
    endpoint_space: dict[str, Any],
    topology_spaces: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    shared_space = {
        "node_count": node_counts,
        "rank_count": rank_counts,
        **global_space,
        **network_space,
        **endpoint_space,
    }

    points: list[dict[str, Any]] = []
    topology_list = list(topologies)

    for _ in range(stochastic_samples):
        topology = _sample_value(topology_list, rng)
        topo_space = topology_spaces[topology]

        shared_point = {
            key: _sample_value(value, rng)
            for key, value in shared_space.items()
        }
        topology_point = {
            key: _sample_value(value, rng)
            for key, value in topo_space.items()
        }

        points.append(
            {
                **shared_point,
                "topology": topology,
                "topology_params": topology_point,
            }
        )

    return points


def _build_run_spec(
    *,
    run_parameters: dict[str, Any],
    experiment_name: str,
    sst_extra_args: list[str],
) -> MerlinRunSpec:
    topology = run_parameters["topology"]
    node_count = int(run_parameters["node_count"])
    rank_count = int(run_parameters["rank_count"])

    config_values: dict[str, Any] = {
        "topology": topology,
        **_extract_scope_values(run_parameters, DEFAULT_GLOBAL_PARAMS.keys()),
        **_extract_scope_values(run_parameters, DEFAULT_NETWORK_PARAMS.keys()),
        **_extract_scope_values(run_parameters, DEFAULT_ENDPOINT_PARAMS.keys()),
        **run_parameters["topology_params"],
    }
    config_values = _normalize_time_fields(config_values)

    run_id = _short_hash(config_values, node_count, rank_count)
    run_name = (
        f"{experiment_name}_{topology}_"
        f"n{node_count}_r{rank_count}_{run_id}"
    )

    launcher = {
        "srun": [
            f"--nodes={node_count}",
            f"--ntasks-per-node={rank_count}",
        ],
        "mpirun": [
            "-n",
            str(node_count * rank_count),
            "-N",
            str(rank_count),
        ],
    }

    sst_args = _build_sst_args(sst_extra_args)

    config_args = _config_tokens_from_values(config_values)

    metadata = {
        "experiment_name": experiment_name,
        "run_name": run_name,
        "run_id": run_id,
        "topology": topology,
        "execution": {
            "node_count": node_count,
            "rank_count": rank_count,
        },
        "parameters": config_values,
    }

    return MerlinRunSpec(
        run_id=run_id,
        run_name=run_name,
        launcher=launcher,
        sst_args=sst_args,
        config_args=config_args,
        metadata=metadata,
    )


def _config_tokens_from_values(config_values: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for key in sorted(config_values.keys()):
        value = config_values[key]
        if value is None or value == "":
            continue
        flag = f"--{key.replace('_', '-')}"
        tokens.extend([flag, str(value)])
    return tokens


def _build_sst_args(sst_extra_args: Sequence[str]) -> list[str]:
    filtered_extra_args = [
        arg
        for arg in sst_extra_args
        if not arg.startswith("--timing-info")
    ]

    return [
        "--timing-info=3",
        "--parallel-load=SINGLE",
        *filtered_extra_args,
    ]


def _normalize_time_fields(config_values: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _normalize_nanoseconds(value)
        if key in TIME_PARAM_KEYS
        else value
        for key, value in config_values.items()
    }


def _normalize_nanoseconds(value: Any) -> Any:
    if value is None or value == "":
        return value

    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return stripped
        if stripped.lower().endswith("ns"):
            return stripped
        if any(char.isalpha() for char in stripped):
            return stripped
        return f"{stripped}ns"

    if isinstance(value, bool):
        return value

    if isinstance(value, Integral):
        return f"{int(value)}ns"

    if isinstance(value, Real):
        return f"{value}ns"

    return value


def _flatten_dict(
    data: dict[str, Any],
    *,
    separator: str,
    prefix: str = "",
) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        flat_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            flattened.update(
                _flatten_dict(value, separator=separator, prefix=flat_key)
            )
        else:
            flattened[flat_key] = value
    return flattened


def _extract_scope_values(
    run_parameters: dict[str, Any],
    keys: Sequence[str],
) -> dict[str, Any]:
    return {
        key: run_parameters[key]
        for key in keys
    }


def _short_hash(config_values: dict[str, Any], *values: Any) -> str:
    blob = json.dumps(
        {
            "config_values": config_values,
            "execution_values": values,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:10]


def _cartesian_product_dict(space: dict[str, Any]) -> list[dict[str, Any]]:
    normalized = {
        key: _normalize_for_deterministic(value)
        for key, value in space.items()
    }
    keys = list(normalized.keys())
    values = [normalized[key] for key in keys]

    points: list[dict[str, Any]] = []
    for combo in itertools.product(*values):
        points.append(dict(zip(keys, combo)))
    return points


def _normalize_for_deterministic(value: Any) -> list[Any]:
    if _is_sequence(value):
        normalized = list(value)
        if len(normalized) == 0:
            raise ValueError("Parameter list cannot be empty")
        return normalized
    return [value]


def _sample_value(value: Any, rng: random.Random) -> Any:
    if _is_sequence(value):
        values = list(value)
        if len(values) == 0:
            raise ValueError("Parameter list cannot be empty")

        if len(values) == 2 and _is_numeric(values[0]) and _is_numeric(values[1]):
            lower = values[0]
            upper = values[1]
            if lower > upper:
                raise ValueError("Stochastic range lower bound is greater than upper bound")

            if isinstance(lower, Integral) and isinstance(upper, Integral):
                return rng.randint(int(lower), int(upper))
            return rng.uniform(float(lower), float(upper))

        return rng.choice(values)

    return value


def _with_defaults(defaults: dict[str, Any], overrides: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(defaults)
    if not overrides:
        return merged

    unknown = set(overrides.keys()) - set(defaults.keys())
    if unknown:
        raise ValueError(f"Unknown parameter overrides: {sorted(unknown)}")

    merged.update(overrides)
    return merged


def _validate_topologies(topologies: Sequence[str]) -> None:
    if len(topologies) == 0:
        raise ValueError("topologies must not be empty")

    unknown = [topology for topology in topologies if topology not in TOPOLOGY_VALUES]
    if unknown:
        raise ValueError(f"Unknown topologies: {unknown}")


def _validate_positive_int_list(name: str, values: Sequence[int]) -> None:
    if len(values) == 0:
        raise ValueError(f"{name} must not be empty")
    if any(value <= 0 for value in values):
        raise ValueError(f"{name} entries must be positive")


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _is_numeric(value: Any) -> bool:
    return isinstance(value, Real)
