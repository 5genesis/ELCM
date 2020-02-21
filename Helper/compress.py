from typing import List
import zipfile
from os.path import abspath, dirname


class Compress:
    @staticmethod
    def Zip(files: List[str], output: str) -> None:
        output = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)

        files = [abspath(file) for file in files]
        rootFolder = Compress.getRootPath(files)

        for file in files:
            file = abspath(file)
            archiveName = file.replace(rootFolder, '')
            output.write(file, archiveName)

        output.close()

    @staticmethod
    def getRootPath(files: List[str]) -> str:
        def iterator(fs: List[str]):
            for f in zip(*fs):
                if f.count(f[0]) == len(f):
                    yield f[0]
                else:
                    return

        if len(files) == 1:
            return dirname(files[0])
        else:
            return ''.join(iterator(files))