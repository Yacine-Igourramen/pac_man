import json
import sys
from dataclasses import dataclass, field


@dataclass
class Config:
    """Holds all config keys required."""

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


def validate_config(config: Config) -> None:
    """Check config values for minimums, types, and negative numbers."""
    if (
        not isinstance(config.highscore_filename, str)
        or not config.highscore_filename.strip()
    ):
        raise ValueError("highscore_filename must be a non-empty string")

    # Values that must be strictly > 0
    positive_fields = {
        "lives": config.lives,
        "pacgum": config.pacgum,
        "level_max_time": config.level_max_time,
    }
    for key, val in positive_fields.items():
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
            raise ValueError(
                f"'{key}' must be an integer greater than 0, instead got {val}"
            )

    # Values that must be >= 0 (no negatives)
    non_negative_fields = {
        "points_per_pacgum": config.points_per_pacgum,
        "points_per_super_pacgum": config.points_per_super_pacgum,
        "points_per_ghost": config.points_per_ghost,
        "seed": config.seed,
    }
    for key, val in non_negative_fields.items():
        if not isinstance(val, int) or isinstance(val, bool) or val < 0:
            raise ValueError(f"'{key}' cannot be negative, got {val}")

    # Levels check
    if not isinstance(config.levels, list) or len(config.levels) == 0:
        raise ValueError("levels must be a non-empty list")

    for i, lvl in enumerate(config.levels):
        if (
            not isinstance(lvl, dict)
            or "width" not in lvl
            or "height" not in lvl
        ):
            raise ValueError(
                f"Level {i + 1} must be a dict with 'width' and 'height'"
            )
        w, h = lvl["width"], lvl["height"]
        if (
            not isinstance(w, int)
            or not isinstance(h, int)
            or w <= 0
            or h <= 0
        ):
            raise ValueError(
                f"Level {i + 1} width and height must be positive, "
                f"got ({w}, {h})"
            )


def load_config(file_path: str) -> dict:
    """Read file line by line, ignore comment lines, and load JSON."""
    lines = []
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip().startswith("#"):
                lines.append(line)
    return json.loads("".join(lines))


def parser(args: list[str]) -> Config:
    """Check sys.argv, load config, validate values, and return Config."""
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
