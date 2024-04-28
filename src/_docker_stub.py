import sys
import time


def main():
    print(  # noqa: T201
        "You must specify module in command argument, default is current stub module",
        file=sys.stderr,
    )
    time.sleep(60)
    sys.exit(1)


if __name__ == "__main__":
    main()
