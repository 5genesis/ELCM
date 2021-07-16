from typing import Optional
from .metal_requirements import Metal


class NsInfo:
    def __init__(self, nsName: str, nsId: str, location: str):
        self.Name = nsName
        self.Id = nsId
        self.Location = location
        self.SliceId: Optional[str] = None
        self.Requirements = Metal()

    def __repr__(self):
        return f'NS:{self.Name}|{self.Id}@{self.Location} SliceId:{self.SliceId} Req:[{self.Requirements}]'
