import click as c
import dulwich.repo as r
import ogit.logging as ol
import ogit.config as oc


@c.group()
@c.option("--log-level", type=c.Choice(ol.LOG_LEVELS))
@c.pass_context()
def main(ctx: c.Context, log_level: str):
    config = oc.Config(
        logging=oc.LogConfig(
            level=log_level,
        )
    )
    ctx.config = config
    ctx.log = ol.create_logger(config)


@main.command()
@c.argument("msg", nargs=1)
@c.pass_config()
def save(config: oc.Config, msg: c.STRING) -> None:
    c.echo(f"message: {msg}")


if __name__ == "__main__":
    main()
