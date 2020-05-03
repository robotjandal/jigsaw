import numpy as np
from pathlib import Path


class Solver:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        if not self.folder_path.is_dir():
            raise NotADirectoryError
        self.original = None
        self.scrambled = None
        self.ids_original = np.empty
        self.ids_scrambled = np.empty

    def not_implemented_yet(self):
        print(f"In future this section will solve the jigsaw puzzle.")
