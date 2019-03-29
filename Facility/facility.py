from os.path import exists
from shutil import copy
import yaml
from typing import Dict, List


class Facility:
    FILENAME = 'facility.yml'
    data = None

    @classmethod
    def Reload(cls):
        if not exists(cls.FILENAME):
            copy('Facility/default_facility', cls.FILENAME)

        with open(cls.FILENAME, 'r', encoding='utf-8') as file:
            cls.data = yaml.safe_load(file)

    @classmethod
    def GetUEActions(cls, id: str) -> List[Dict]:
        return cls.getFromSection('UEs', id)

    @classmethod
    def GetTestCaseActions(cls, id: str) -> List[Dict]:
        return cls.getFromSection('TestCases', id)

    @classmethod
    def getFromSection(cls, section: str, id: str) -> List[Dict]:
        if cls.data is None: cls.Reload()

        if id in cls.data[section].keys():
            return cls.data[section][id]
        return []
