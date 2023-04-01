from uuid import UUID, uuid4
from dataclasses import dataclass
from click import option, argument, pass_context, pass_obj, Choice, group, Context, STRING
from ogit.log import create_logger, Logger, INFO, LOG_LEVELS, LogLevel
from ogit.config import Config, LogConfig
from dulwich.repo import Repo


@dataclass()
class OgitContext:
    config: Config
    logger: Logger
    correlation_id: UUID
    repo: Repo


@group()
@option("--log-level", type=Choice(LOG_LEVELS), default=INFO)
@pass_context
def main(ctx: Context, log_level: LogLevel):
    config = Config(
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
        correlation_id=uuid4(),
        repo=Repo.discover(),
    )
    logger.info("8cd87b0c-a050-43cb-b33d-214a85b8e97c", "starting now", foo="bar", biz=42)


@main.command()
@argument("msg", nargs=1)
@pass_obj
def save(ctx: OgitContext, msg: STRING) -> None:
    ctx.logger.info("51b4ed78-7067-4943-9278-ad1fcc6806d5", "doin a save", savemsg=msg)


if __name__ == "__main__":
    main()
