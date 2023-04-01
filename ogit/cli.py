from uuid import UUID, uuid4
from dataclasses import dataclass
from click import option, argument, pass_context, pass_obj, Choice, group, Context, STRING, Path
from ogit.log import create_logger, Logger, INFO, LOG_LEVELS, LogLevel
from ogit.config import Config, LogConfig
from dulwich.repo import Repo
from typing import Iterable


@dataclass()
class OgitContext:
    config: Config
    logger: Logger
    repo: Repo


@group()
@option("--log-level", type=Choice(LOG_LEVELS), default=INFO, envvar="LOG_LEVEL")
@pass_context
def main(ctx: Context, log_level: LogLevel):
    config = Config(
        correlation_id=uuid4(),
        logging=LogConfig(
            level=log_level,
            filters=[],
            sinks="seq",
            file=None,
        )
    )
    logger = create_logger(config)
    ctx.obj = OgitContext(
        config=config,
        logger=logger,
        repo=Repo.discover(),
    )
    logger.info("8cd87b0c-a050-43cb-b33d-214a85b8e97c", "Start main execution")


@main.command()
@argument("msg", nargs=1, required=True)
@argument("files", nargs=-1, type=Path(exists=True, writable=False, allow_dash=False))
@pass_obj
def save(ctx: OgitContext, msg: STRING, files: Iterable[str]) -> None:
    files = list(files)
    ctx.logger.info("51b4ed78-7067-4943-9278-ad1fcc6806d5", "Adding and committing files", {"msg": msg, "files": files})


if __name__ == "__main__":
    main()
