import dataclasses


@dataclasses.dataclass(frozen=True)
class SSTParamSet:
    name: str
    node_count: int
    ranks_per_node: int
    threads_per_rank: int
    width: int
    height: int
    event_density: float
    time_to_run: int
    ring_size: int
    small_payload: int
    large_payload: int
    large_event_fraction: float
    imbalance_factor: float
    component_size: int

    @property
    def simulation_flags(self) -> tuple[str, ...]:
        return (
            "--height",
            str(self.height),
            "--width",
            str(self.width),
            "--eventDensity",
            str(self.event_density),
            "--timeToRun",
            f"{self.time_to_run}ns",
            "--numRings",
            str(self.ring_size),
            "--smallPayload",
            str(self.small_payload),
            "--largePayload",
            str(self.large_payload),
            "--largeEventFraction",
            str(self.large_event_fraction),
            "--imbalance-factor",
            str(self.imbalance_factor),
            "--componentSize",
            str(self.component_size),
        )

    @property
    def sst_flags(self) -> tuple[str, ...]:
        return (
            "--num-threads",
            str(self.threads_per_rank),
            "--print-timing-info=3",
            "--parallel-load=SINGLE",
        )

    def as_param_str(self, *, sep: str = "-") -> str:
        return sep.join(
            (
                str(self.name),
                str(self.node_count),
                str(self.ranks_per_node),
                str(self.threads_per_rank),
                str(self.width),
                str(self.height),
                str(self.event_density),
                str(self.ring_size),
                str(self.time_to_run),
                str(self.small_payload),
                str(self.large_payload),
                str(self.large_event_fraction),
                str(self.imbalance_factor),
                str(self.component_size),
            )
        )
