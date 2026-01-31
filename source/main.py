import frggj
from frggj.api.engine import GEngine


def main():
    execution_path = frggj.__path__[0]
    GEngine(execution_path, False)


if __name__ == "__main__":
    main()
