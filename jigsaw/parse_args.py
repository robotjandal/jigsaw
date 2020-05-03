import argparse


def parse_args(argv=None):
    """
        taking CMD arguments and sending them through the argument
        parser.
    """
    parser = argparse.ArgumentParser(prog="jigsaw")
    # parser.add_argument('action', help='Action to be completed')
    subparsers = parser.add_subparsers(
        dest="action", help="commands", required=True
    )
    # create action
    create_parser = subparsers.add_parser(
        "create", help="Create an jigsaw using supplied image"
    )
    create_parser.add_argument("image_path", help="Path to image")
    # solve action
    solve_parser = subparsers.add_parser("solve", help="Solve jigsaw image")
    solve_parser.add_argument("folder_path", help="Path to scrambled image folder")
    return parser.parse_args(argv)
