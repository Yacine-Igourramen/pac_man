import sys
from parser import parser
sys.path.append("mazegenerator-00001/mazegenerator-2.1.0-py3-none-any")
from mazegenerator import MazeGenerator


def main():
    """entry point"""
    arguments = sys.argv
    config = parser(arguments)

    ma = MazeGenerator()
    ma.generate(config.seed)
    print(ma.maze)


if __name__ == "__main__":
    main()
