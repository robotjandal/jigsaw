""" This file contains shared classes and functions.
    * yamlFileIO returns the contents of the config.yaml file as a dict
    * CSVFileIO is used to read from or write to a .csv file.
"""
import logging
import os
from pathlib import Path
import yaml
import csv
import numpy as np
import shutil


class CSVFileIO:
    """
        This class is used to read and write to data to and from a
        chosen csv file.
    """

    def __init__(self, folder, csvfile, fieldnames):
        self.data = []
        self.fieldnames = fieldnames
        path = os.path.join(os.getcwd(), "data")
        path = os.path.join(path, folder)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, csvfile)
        self.path = Path(path)

    def read_dict(self):
        """
            Reads the entire csv file.
        """
        output = []
        if self.path.exists() is False:
            return None
        with open(self.path, mode="r") as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=self.fieldnames)
            for row in reader:
                output.append(row)
        return output
        # self.data.clear()
        # # self.data = pandas.read_csv(self.path, index_col='path')
        # logging.debug('Rows: read: %i', len(self.data))
        # return self.data

    def write_dict(self, data):
        """
        """
        if data is None:
            os.remove(self.path)
        with open(self.path, mode="w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)


class FileIO:
    """
        Read and write to a custom file format.
    """

    def __init__(self, folder, file_path):
        path = os.path.join(os.getcwd(), "data")
        path = os.path.join(path, folder)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, file_path)
        self.path = Path(path)

    def read_file(self):
        pass

    def write_file(self, data):
        if data is None:
            os.remove(self.path)
        with open(self.path, mode="a") as write_file:
            writer = csv.writer(write_file)

            # custom_file.writelines(data[0])
            for row in data:
                # print(row)
                writer.writerow(row)

    def append_file(self, data):
        pass


class FolderIO:
    def __init__(self, folderpath):
        self.folder = folderpath

    def create(self):
        """
            Creates all nested folders in folderpath.
            If the path already exists it does nothing.
        """
        if not self.exists():
            try:
                os.makedirs(self.folder)
            except OSError:
                print(f"Creation of the directory {self.folder} failed")

    def exists(self):
        return self.folder.is_dir()

    # def delete(self):
    #     if not self.exists():
    #         try:
    #             shutil.rmtree(dir_path)


class YamlFileIO:
    """
        Allows the reading and writing of yaml files including opening a
        parsed object.
    """

    def __init__(self, folder, yamlfile):
        self.data = {}
        self.path = Path(folder, yamlfile)

    def read_yaml(self):
        """
            Reads from yaml file only if the yaml file exists. Otherwise
        it returns without doing anything.
        """
        if not self.path.is_file():
            logging.debug("File not found %s. No action taken", self.path)
            return
        try:
            with self.path.open("r") as f:
                self.data = yaml.safe_load(f)
        except IOError as e_info:
            print(e_info)
            raise
        except yaml.YAMLError as e_info:
            print(f"Failed to import file. \n{e_info}")
            raise

    def write_yaml(self, output):
        """
            Write dictionary object to yaml file.
        """
        # print(self.path)
        # print(Path.cwd())
        try:
            with self.path.open("w+") as f:
                yaml.dump(output, f, default_flow_style=False)
        except IOError as e_info:
            print(e_info)
            raise


class NumpyIO:
    """
        Allows for retrieving and saving of numpy arrays.
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def save(self, array):
        np.save(self.file_path, array)

    def load(self):
        return np.load(self.file_path)
