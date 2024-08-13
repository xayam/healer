import uci


def main() -> None:
    uci_loop = uci.UCI()

    while True:
        command = input()
        uci_loop.process_command(command)

        if command == "quit":
            break


if __name__ == "__main__":
    main()
