from mazegenerator import MazeGenerator

def main():
    ma = MazeGenerator()
    ma.generate(156)
    print(ma.maze)
    print("Hello from pac-man!")


if __name__ == "__main__":
    main()
