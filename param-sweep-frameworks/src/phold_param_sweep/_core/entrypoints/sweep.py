import logging

from phold_param_sweep.parse import parse_arguments

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s | %(message)s"
)


def main() -> int:
    launch_ctx, param_sets = parse_arguments()
    with launch_ctx as ctx:
        for param in param_sets:
            ctx.launch(param)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
