from src.utils.logger.logger import Logger

log = Logger("telegram-utils")


def command_args_to_dict(args: str) -> dict[str, str]:
    try:
        return dict([pair.split("=") for pair in args.split()])
    except Exception as e:
        log.error(f"failed to parse command args: {e}")
        return {}
