import sys
from src.bot import NeilBot


def main():
    if len(sys.argv) <= 1:
        raise "Environment not specified. Specify by passing 'test' or 'prod'"

    if sys.argv[1] == 'test':
        print('test')

    elif sys.argv[1] == 'prod':
        # TODO: run at the end of each day

        # TODO: get data of past 10 days before today
        print('prod')

    # compare the

    # evaluate the current step should be
    return 0


if __name__ == '__main__':
    main()
