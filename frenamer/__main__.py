import typer
import re
from frenamer import app, version
import requests

try:
    latest_version = re.search(
        r'^version\s*=\s*"(.*)".*$',
        requests.get(
            "https://raw.githubusercontent.com/TheAwiteb/frenamer/master/frenamer/version.py"
        ).text,
        flags=re.MULTILINE,
    ).group(1)
    if latest_version != version:
        typer.echo(
            typer.style(
                f"\nYour version of frenamer is old. The latest version of frenamer is {latest_version}, and your version is {version}.\nIf you want to update to it, run the following command\n",
                fg="yellow",
            )
            + "$ python3 -m pip install frenamer --upgrade"
        )
except Exception:
    pass

if __name__ == "__main__":
    app()
