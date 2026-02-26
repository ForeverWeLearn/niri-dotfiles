#!/bin/python
import sys
import json
import subprocess
import argparse
from pathlib import Path

CONFIG_FILE = Path("~/.config/niri/extend/animations.kdl").expanduser()

ANIME_COFFEE = "Coffee"
ANIME_CHILL = "Chill"
ANIME_SPRING = "Spring"
ANIMES = [
    ANIME_COFFEE,
    ANIME_CHILL,
    ANIME_SPRING,
]
KDL_NAME_MAP = {
    ANIME_COFFEE: "coffee-animations",
    ANIME_CHILL: "chill-animations",
    ANIME_SPRING: "spring-animations",
}


def send_toast(anime: str):
    data = json.dumps(
        {
            "title": "Animation",
            "body": anime,
        }
    )
    subprocess.run(f"qs -c noctalia-shell ipc call toast send '{data}'", shell=True)


def update_animations(anime: str):
    if anime not in ANIMES:
        return

    with open(CONFIG_FILE, "w") as config:
        config.write(f'include "./{KDL_NAME_MAP[anime]}.kdl";')

    send_toast(anime)


parser = argparse.ArgumentParser(
    description=f"Change niri animations. Example: `anime.py {ANIME_COFFEE}`"
)
parser.add_argument("name", help=f"{' | '.join(ANIMES)}")

if len(sys.argv) == 1:
    parser.print_help(sys.stdout)
    sys.exit(1)

args = parser.parse_args()
anime = args.name

if anime not in ANIMES:
    parser.print_help(sys.stdout)
    sys.exit(1)


update_animations(anime)
