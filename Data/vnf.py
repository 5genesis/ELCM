from Helper import Serialize
from typing import Dict


class Vnf:
    def __init__(self, data: Dict):
        self.Id, self.Name, self.Description = Serialize.Unroll(data, "Id", "Name", "Description")
        self.Vnfd, self.Image, self.Location = Serialize.Unroll(data, "VNFD", "Image", "Location")
