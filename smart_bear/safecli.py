import webbrowser

import arrow
import typer

from smart_bear.bear.x_callback_url import add_text

app = typer.Typer()


@app.command()
def wip(text: str):
    time = arrow.now().format("YYYY-MM-DD HH:mm")
    output = f"\n{time}\n{text}"
    url = add_text(title="WIP", text=output).url
    webbrowser.open(url)
    typer.echo(f"Saved {text}")


if __name__ == "__main__":
    app()
