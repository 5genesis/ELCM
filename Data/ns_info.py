from typing import Optional
from .metal_requirements import Metal


class NsInfo:
    def __init__(self, nsId: str):
        self.Id = nsId
        self.Location: Optional[str] = None
        self.SliceId: Optional[str] = None
        self.Requirements = Metal()
