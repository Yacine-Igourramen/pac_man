import json
import sys
from dataclasses import dataclass, field

# @property is just so that u can use methods as
# attributes and call them as such


@dataclass
class Config:
    """holds all config keys required"""

    highscore_filename: str = "highscores.json"
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    levels: list = field(default_factory=list)

    @property
    def pts_per_pg(self) -> int:
        return self.points_per_pacgum

    @property
    def pts_per_super_pg(self) -> int:
        return self.points_per_super_pacgum


# func that handles all stupid input 

def validate_config(config: Config) -> None:
    """hecks config values and clamps invalid inputs to safe defaults"""
    default_levels = [
        {"width": 19, "height": 21},
        {"width": 19, "height": 21},
        {"width": 21, "height": 21},
        {"width": 21, "height": 23},
        {"width": 23, "height": 23},
        {"width": 23, "height": 25},
        {"width": 25, "height": 25},
        {"width": 27, "height": 27},
        {"width": 29, "height": 29},
        {"width": 31, "height": 31},
    ]

    if (
        not isinstance(config.highscore_filename, str)
        or not config.highscore_filename.strip()
    ):
        print(
            f"[WARNING] 'highscore_filename' must be a non-empty string "
            f"(got {config.highscore_filename!r}), defaulting to 'highscores.json'"
        )
        config.highscore_filename = "highscores.json"

    # values that must be strictly > 0
    positive_defaults = {
        "lives": 3,
        "pacgum": 42,
        "level_max_time": 90,
    }
    for key, default in positive_defaults.items():
        val = getattr(config, key)
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
            print(
                f"[WARNING] '{key}' must be an integer greater than 0, "
                f"got {val}. Defaulting to {default}"
            )
            setattr(config, key, default)

    # values that must be >= 0
    non_negative_defaults = {
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "seed": 42,
    }
    for key, default in non_negative_defaults.items():
        val = getattr(config, key)
        if not isinstance(val, int) or isinstance(val, bool) or val < 0:
            print(
                f"[WARNING] '{key}' cannot be negative, got {val}. "
                f"Defaulting to {default}"
            )
            setattr(config, key, default)

    # levels check
    if not isinstance(config.levels, list) or len(config.levels) == 0:
        print("[WARNING] 'levels' must be a non-empty list, using default levels")
        config.levels = [lvl.copy() for lvl in default_levels]

    for i, lvl in enumerate(config.levels):
        if (
            not isinstance(lvl, dict)
            or "width" not in lvl
            or "height" not in lvl
        ):
            print(
                f"[WARNING] Level {i + 1} must be a dict with 'width' and 'height', "
                f"defaulting to 19x21"
            )
            config.levels[i] = {"width": 19, "height": 21}
            continue

        w, h = lvl.get("width"), lvl.get("height")
        if not isinstance(w, int) or isinstance(w, bool) or w <= 0:
            print(
                f"[WARNING] Level {i + 1} width must be positive, "
                f"got {w}. Defaulting to 19"
            )
            lvl["width"] = 19
        if not isinstance(h, int) or isinstance(h, bool) or h <= 0:
            print(
                f"[WARNING] Level {i + 1} height must be positive, "
                f"got {h}. Defaulting to 21"
            )
            lvl["height"] = 21


def load_config(file_path: str) -> dict:
    """read file line by line, ignore comment lines, and load json"""
    lines = []
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip().startswith("#"):
                lines.append(line)
    return json.loads("".join(lines))


def parser(args: list[str]) -> Config:
    """checks sysargv, load config, validate values, and return config"""
    if len(args) != 2 or not args[1].endswith(".json"):
        print("[ERROR] Usage: python3 main.py <config.json>")
        sys.exit(1)

    data = load_config(args[1])

    cfg = Config(
        highscore_filename=data.get("highscore_filename", "highscores.json"),
        lives=data.get("lives", 3),
        pacgum=data.get("pacgum", 42),
        points_per_pacgum=data.get("points_per_pacgum", 10),
        points_per_super_pacgum=data.get("points_per_super_pacgum", 50),
        points_per_ghost=data.get("points_per_ghost", 200),
        seed=data.get("seed", 42),
        level_max_time=data.get("level_max_time", 90),
        levels=data.get("levels", []),
    )

    validate_config(cfg)
    return cfg
