import typer

from promptvc.commands import (
    add,
    commit,
    diff,
    env,
    export,
    init,
    list_prompts,
    log,
    pull,
    push,
    rollback,
    search,
    show,
    tag,
)

app = typer.Typer(
    name="promptvc",
    help="[bold]Git for your prompts.[/bold] Version, diff, rollback, and ship prompts like code.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

app.command("init")(init.run)
app.command("add")(add.run)
app.command("commit")(commit.run)
app.command("log")(log.run)
app.command("show")(show.run)
app.command("diff")(diff.run)
app.command("rollback")(rollback.run)
app.command("list")(list_prompts.run)
app.command("env")(env.run)
app.command("export")(export.run)
app.command("tag")(tag.run)
app.command("search")(search.run)
app.command("push")(push.run)
app.command("pull")(pull.run)

if __name__ == "__main__":
    app()
