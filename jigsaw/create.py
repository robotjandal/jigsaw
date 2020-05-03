import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from jigsaw.fileIO import YamlFileIO, FolderIO, NumpyIO


class Creator:
    def __init__(self, image_path):
        """
        @param image_path: image path to be loaded

        Use process() to start the program
        """
        self.image_path = Path(image_path)
        self.output_folder = Path("output/" + self.image_path.stem)
        self.image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if self.image is None:
            raise FileNotFoundError("Supplied path is not an image")
        self.yaml = {}
        self.original = None
        self.scrambled = None
        self.ids_original = np.empty
        self.ids_scrambled = np.empty

    def process(self):
        """
            Creates a scrambled image based on the original image, an associated yaml
            file and numpy data files to make it easier to solve the scrambled
            image.
        """
        self.analyse_image()
        properties = self.optimise_squares()
        self.randomise_ids(properties)
        self.size_image(properties)
        self.scramble_image(properties)
        self.save()

    def analyse_image(self):
        """
            Collate information about the image to be saved to yaml file
        """
        self.yaml["filename"] = self.image_path.name
        now = datetime.now()
        self.yaml["created"] = now.strftime("%Y-%m-%d %H:%M:%S")

    def optimise_squares(self):
        """
            Maximise coverage of the squares over the provided image
        """
        squares = 1000
        properties = maximise_square_coverage(
            squares, self.image.shape[0], self.image.shape[1]
        )
        self.yaml["squares"] = squares
        self.yaml["dimensions"] = (
            properties["dimensions"].y,
            properties["dimensions"].x,
        )
        self.yaml["rows"] = properties["rows"]
        self.yaml["cols"] = properties["cols"]
        return properties

    def randomise_ids(self, properties):
        """
            Given some set parameters scramble the location and in future (orientation)
            of small sqaures.
        """
        self.ids_original = np.arange(properties["squares"]).reshape(
            (properties["rows"], properties["cols"])
        )
        result = self.ids_original.flatten()
        np.random.shuffle(result)
        self.ids_scrambled = result.reshape(properties["rows"], properties["cols"])

    def size_image(self, properties):
        """
            Both the original and shrunk image should be the same size.
            This size is defined by the properties from optimise_squares
        """

        self.original = self.image[
            0 : properties["rows"] * properties["dimensions"].y,
            0 : properties["cols"] * properties["dimensions"].x,
        ].copy()
        self.scrambled = self.image[
            0 : properties["rows"] * properties["dimensions"].y,
            0 : properties["cols"] * properties["dimensions"].x,
        ].copy()

    def scramble_image(self, properties):
        """
            Using the id positions in ids_original the input image is rearranged to
            scrambled_image
        """
        for i in range(0, properties["squares"]):
            ori = np.where(self.ids_original == i)
            scr = np.where(self.ids_scrambled == i)
            move = MoveSquare(
                self.original, Position(ori[0][0], ori[1][0]), properties["dimensions"]
            )
            move.apply(self.scrambled, Position(scr[0][0], scr[1][0]))

    def save(self):
        """
            save images, numpy data arrays and a yaml file to folder.
            Foldername is based on the image name.
            Other file names can be found using the yaml file.
        """
        make_folder = FolderIO(self.output_folder)
        make_folder.create()
        writer = YamlFileIO(self.output_folder, "create.yaml")
        writer.write_yaml(self.yaml)
        cv2.imwrite(str(self.output_folder / self.image_path.name), self.original)
        cv2.imwrite(
            str(self.output_folder / f"{self.image_path.name}_scrambled"),
            self.scrambled,
        )
        if self.output_folder.exists():
            or_io = NumpyIO(self.output_folder / "original")
            sc_io = NumpyIO(self.output_folder / "scrambled")
            or_io.save(self.ids_original)
            sc_io.save(self.ids_scrambled)


class MoveSquare:
    def __init__(self, original, position, dimensions):
        """
            From the original image a rectangle segment is extracted using the position
            and dimensions of the rectangle.
            The segment can then be applied to anothe image.
        """
        start_pixel = Pixel(position.y * dimensions.y, position.x * dimensions.x)
        self.square = original[
            start_pixel.y : start_pixel.y + dimensions.y,
            start_pixel.x : start_pixel.x + dimensions.x,
        ]
        self.dimensions = dimensions

    def apply(self, image, position):
        """
            The image segment taken from the previous image is applied to the supplied
            image at a given position.
        """
        start_pixel = Pixel(
            position.y * self.dimensions.y, position.x * self.dimensions.x,
        )
        image[
            start_pixel.y : start_pixel.y + self.dimensions.y,
            start_pixel.x : start_pixel.x + self.dimensions.x,
        ] = self.square
        return image


def find_factors(num):
    """
    Find all factors for a number returned using zip.
    The factors are organised in pairs with the low value first
    """
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    first = factors[: len(factors) // 2]
    second = factors[len(factors) // 2 :]
    second.reverse()
    return zip(first, second)


def maximise_square_coverage(squares, img_height, img_width):
    """
        Find the maximum amount of an image to be covered by a given number of squares,
        image height and Pixel width.
        The following properties are returned based on the squares:
            * number of rows
            * number of columns
            * square length

        Each factor pair attempts to maximise the % of the image and the best
        pair and associated square length is returned.
    """
    properties = {}
    factors = find_factors(squares)
    # square length is based on the dimension with the highest number of pixels
    square_length = img_height if img_height > img_width else img_width
    max_area = 0
    for low_factor, high_factor in factors:
        length = square_length // high_factor
        jigsaw_size = [length * high_factor, length * low_factor]
        area = jigsaw_size[0] * jigsaw_size[1]
        if area > max_area:
            max_area = area
            max_length = length
            maximised_factors = (
                [high_factor, low_factor]
                if img_height > img_width
                else [low_factor, high_factor]
            )
    dimensions = Dimension(max_length, max_length)
    properties = {
        "squares": squares,
        "dimensions": dimensions,
        "rows": maximised_factors[0],
        "cols": maximised_factors[1],
    }
    return properties


class Position:
    def __init__(self, y, x, direction=None):
        if x < 0 or y < 0:
            raise NotImplementedError
        self.y = y
        self.x = x
        self.direction = direction
        if self.direction is None:
            self.direction = 0


class Dimension:
    def __init__(self, y, x):
        if x < 0 or y < 0:
            raise ValueError
        self.y = y
        self.x = x


class Pixel:
    def __init__(self, y, x):
        if x < 0 or y < 0:
            raise ValueError
        self.y = y
        self.x = x

    def __repr__(self):
        return repr(f"y: {self.y}, x: {self.x}")
