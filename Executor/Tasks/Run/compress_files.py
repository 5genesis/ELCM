from Task import Task
from Helper import Level
from os.path import abspath, join, isdir, isfile
from os import listdir
from typing import List


class CompressFiles(Task):
    def __init__(self, logMethod, params):
        super().__init__("Compress Files", params, logMethod, None)

    @classmethod
    def listFiles(cls, path) -> List[str]:
        return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    @classmethod
    def listFolders(cls, path) -> List[str]:
        return [join(path, f) for f in listdir(path) if isdir(join(path, f))]

    @classmethod
    def getAllFiles(cls, path) -> List[str]:
        res = []

        for folder in cls.listFolders(path):
            res.extend(cls.getAllFiles(folder))
        for file in cls.listFiles(path):
            res.append(file)

        return res

    def Run(self):
        from Helper import Compress

        files = [abspath(f) for f in self.params.get("Files", [])]
        folders = [abspath(f) for f in self.params.get("Folders", [])]
        output = self.params.get("Output", "")
        self.Log(Level.INFO, f"Compressing files to output: {output}")

        for folder in folders:
            files.extend(self.getAllFiles(folder))

        self.Log(Level.DEBUG, f"Files to compress: {files}")

        try:
            Compress.Zip(files, output)
            self.Log(Level.INFO, "File created")
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while creating zip file: {e}")







