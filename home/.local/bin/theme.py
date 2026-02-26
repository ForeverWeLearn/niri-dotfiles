#!/bin/python
import sys
import argparse
import configparser
import os
import subprocess
from io import StringIO
from pathlib import Path

import json5

WALLPAPER_BASE_DIR = Path("~/Pictures/Wallpapers").expanduser()
WALLPAPER_TARGET_SYMLINK = WALLPAPER_BASE_DIR / "Current"
VSCODE_SETTINGS_PATH = Path("~/.config/Code/User/settings.json").expanduser()
BTOP_SETTINGS_PATH = Path("~/.config/btop/btop.conf").expanduser()
STARSHIP_THEMES_SOURCE = Path("~/.config/starship").expanduser()
STARSHIP_SETTINGS_PATH = Path("~/.config/starship.toml").expanduser()

THEME_CATPPUCCIN = "Catppuccin"
THEME_GRUVBOX = "Gruvbox"
THEME_EVERFOREST = "Everforest"
THEMES = [THEME_CATPPUCCIN, THEME_GRUVBOX, THEME_EVERFOREST]

NOCTALIA_THEME_MAP = {
    THEME_CATPPUCCIN: "Catppuccin",
    THEME_GRUVBOX: "Gruvbox",
    THEME_EVERFOREST: "Everforest",
}

VSCODE_THEME_MAP = {
    THEME_CATPPUCCIN: "Catppuccin Mocha",
    THEME_GRUVBOX: "Gruvbox Dark Medium",
    THEME_EVERFOREST: "Everforest Pro Dark Vibrant",
}

BTOP_THEME_MAP = {
    THEME_CATPPUCCIN: "catppuccin_mocha",
    THEME_GRUVBOX: "gruvbox_material_dark",
    THEME_EVERFOREST: "everforest-dark-medium",
}


def update_noctalia_theme(theme: str):
    subprocess.run(
        f'qs -c noctalia-shell ipc call colorScheme set "{theme}"',
        shell=True,
    )


def update_btop_theme(theme: str):
    if not os.path.exists(BTOP_SETTINGS_PATH):
        print(f"[!!] btop config not found at {BTOP_SETTINGS_PATH}")
        return

    try:
        config = configparser.ConfigParser(interpolation=None)

        with open(BTOP_SETTINGS_PATH, "r") as f:
            config_string = "[root]\n" + f.read()

        config.read_string(config_string)

        if config.get("root", "color_theme") == f'"{theme}"':
            return

        config.set("root", "color_theme", f'"{theme}"')

        with open(BTOP_SETTINGS_PATH, "w") as f:
            out = StringIO()
            config.write(out)
            content = out.getvalue().replace("[root]\n", "", 1).strip()
            f.write(content + "\n")

        print(f"btop: '{theme}'")

    except Exception as e:
        print(f"[!!] btop update failed: {e}")


def update_starship_theme(theme_id: str):
    theme_file = STARSHIP_THEMES_SOURCE / f"{theme_id}.toml"
    subprocess.run(f'ln -srfn "{theme_file}" "{STARSHIP_SETTINGS_PATH}"', shell=True)


def update_vscode_theme(theme: str):
    try:
        with open(VSCODE_SETTINGS_PATH, "r") as f:
            data = json5.load(f)

        if data.get("workbench.colorTheme") == theme:
            return

        data["workbench.colorTheme"] = theme
        with open(VSCODE_SETTINGS_PATH, "w") as f:
            json5.dump(data, f, indent=4, quote_keys=True)
        print(f"VSCode: '{theme}'")
    except Exception as e:
        print(f"[!!] VSCode update failed: {e}")


def update_themes(theme_id: str):
    update_noctalia_theme(NOCTALIA_THEME_MAP[theme_id])
    update_btop_theme(BTOP_THEME_MAP[theme_id])
    update_starship_theme(theme_id)
    update_vscode_theme(VSCODE_THEME_MAP[theme_id])


def update_wallpaper(theme_id: str):
    wallpaper_dir = WALLPAPER_BASE_DIR / theme_id
    if not os.path.exists(wallpaper_dir):
        print(f"[!] Directory {wallpaper_dir} does not exist.")
        return

    subprocess.run(
        f'ln -srfn "{wallpaper_dir}" "{WALLPAPER_TARGET_SYMLINK}"',
        shell=True,
    )
    subprocess.run("rdwal")


parser = argparse.ArgumentParser(
    description=f"Change desktop theme. Example: `theme.py {THEME_CATPPUCCIN}`"
)
parser.add_argument("name", nargs="+", help=f"{' | '.join(THEMES)}")

if len(sys.argv) == 1:
    parser.print_help(sys.stdout)
    sys.exit(1)

args = parser.parse_args()
theme_id = " ".join(args.name)

if theme_id not in THEMES:
    parser.print_help()
    sys.exit(1)


update_themes(theme_id)
update_wallpaper(theme_id)
