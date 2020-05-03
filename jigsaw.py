#!/usr/bin/python3

import logging
from jigsaw.create import Creator
from jigsaw.solve import Solver
from jigsaw.parse_args import parse_args

logging.basicConfig(filename=("logs/jigsawsolver.log"), level=logging.DEBUG)


if __name__ == "__main__":
    args = parse_args()
    if args.action == "create":
        creator = Creator(args.image_path)
        creator.process()
    elif args.action == "solve":
        solver = Solver(args.folder_path)
        solver.not_implemented_yet()
    print("Success")
