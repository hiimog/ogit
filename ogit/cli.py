import os
from uuid import UUID, uuid4
from dataclasses import dataclass
from click import option, argument, pass_context, pass_obj, Choice, group, Context, STRING, Path, BOOL
from ogit.log import create_logger, Logger, INFO, LOG_LEVELS, LogLevel
from ogit.config import Config, LogConfig
import dulwich.porcelain as dul
from typing import Iterable


@dataclass()
class OgitContext:
    config: Config
    logger: Logger
    repo: dul.Repo


trailing_files = argument("files", nargs=-1, type=Path(exists=True, writable=False, allow_dash=False))


@group()
@option("--log-seq/--no-log-seq", default=True, help="Should logs be written to local seq server")
@option("--log-level", type=Choice(LOG_LEVELS), default=INFO, envvar="LOG_LEVEL", help="Verbosity of logs")
@option("--log-file", type=Path(dir_okay=False, writable=True), help="If provided, logging will log to this file")
@pass_context
def main(ctx: Context,
         log_seq: bool,
         log_level: LogLevel,
         log_file: str,
         ):
    sinks = []
    if log_seq:
        sinks.append("seq")
    if log_file:
        sinks.append("file")
    config = Config(
        correlation_id=uuid4(),
        logging=LogConfig(
            level=log_level,
            file=log_file,
            sinks=sinks,
        )
    )
    logger = create_logger(config)
    ctx.obj = OgitContext(
        config=config,
        logger=logger,
        repo=dul.Repo.discover(),
    )
    logger.info("8cd87b0c-a050-43cb-b33d-214a85b8e97c", "Start main execution")


@main.command()
@trailing_files
@pass_obj
def discard(ctx: OgitContext,
            files: Iterable[str]):
    files = list(files or [])


@main.command()
@option("--all", "is_all", default=False, help="Remove all untracked files")
@option("--ignored/--no-ignored", default=False, help="Include ignored files when removing all untracked files")
@trailing_files
@pass_obj
def rmuntracked(ctx: OgitContext,
                is_all: bool,
                ignored: bool,
                files: Iterable[str]):
    files = set(files or [])
    ctx.logger.info("b920c30d-502b-4b21-b135-4a7c6628387f", "Removing untracked files", {
        "all": is_all,
        "ignored": ignored,
        "files": list(files),
    })
    status = dul.status(ctx.repo, ignored, "all")
    untracked_files = set([b.decode("utf-8") for b in status.untracked])
    to_remove = untracked_files if is_all else files
    to_remove.intersection_update(untracked_files)
    ctx.logger.info("3261ece9-72cc-47aa-b5f2-34a8cfd2dbf9", "Untracked files to remove", {
        "files": list(to_remove)
    })


@main.command()
@option("--show-ignored/--no-ignored", default=False)
@option("--show-untracked/--no-untracked", default=True)
@option("-e", "--ext", "file_extensions", multiple=True, required=False, type=STRING)
@trailing_files
@pass_obj
def status(ctx: OgitContext,
           show_ignored: bool,
           show_untracked: bool,
           file_extensions: list[str] | None,
           files: Iterable[str]) -> None:
    requested_files = list(files or [])
    ctx.logger.info("a71b6990-7aad-48af-ab91-6a460a4f385a", "Printing status", {
        "show_ignored": show_ignored,
        "show_untracked": show_untracked,
        "file_extensions": file_extensions,
        "requested_files": requested_files,
    })
    repo = ctx.repo
    show_untracked_str = "all" if show_untracked else "no"
    status = dul.status(repo, show_ignored, show_untracked_str)
    unstaged = [b.decode("utf-8") for b in status.unstaged]
    untracked = [b.decode("utf-8") for b in status.untracked]
    staged = {
        "added": [b.decode("utf-8") for b in status.staged["add"]],
        "modified": [b.decode("utf-8") for b in status.staged["modify"]],
        "deleted": [b.decode("utf-8") for b in status.staged["delete"]],
    }
    ctx.logger.info_lazy("934261e2-ccdf-470d-a8c5-96ace0faca56", lambda: ("Raw status acquired", {
        "unstaged": unstaged,
        "untracked": untracked,
        "staged": staged,
    }))


@main.command()
@option("--amend/--no-amend", default=False)
@argument("msg", nargs=1, required=True)
@trailing_files
@pass_obj
def cam(ctx: OgitContext, amend: bool, msg: STRING, files: Iterable[str]) -> None:
    files = list(files)
    ctx.logger.info("51b4ed78-7067-4943-9278-ad1fcc6806d5", "Adding and committing files",
                    {"msg": msg, "files": files, "amend": amend})


if __name__ == "__main__":
    main()
