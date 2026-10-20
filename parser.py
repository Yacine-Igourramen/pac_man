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


def load_config(file_path: str) -> dict:
    """load file"""
    lines = []
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip().startswith("#"):
                lines.append(line)
    return json.loads("".join(lines))


def parser(args: list[str]) -> Config:
    """heck sysargv amd return Config"""
    if len(args) != 2 or not args[1].endswith(".json"):
        print("[ERROR] Usage: python3 main.py <config.json>")
        sys.exit(1)

    data = load_config(args[1])

    return Config(
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