# import tensorflow as tf
# tf.get_logger().setLevel('ERROR')
#
# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

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
