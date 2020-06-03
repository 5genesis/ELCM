class Metal:
    def __init__(self, cpu: int = 0, ram: float = 0, disk: float = 0):
        self.Cpu = cpu
        self.Ram = ram
        self.Disk = disk

    def __str__(self):
        return f"C:{self.Cpu} R:{self.Ram} S:{self.Disk}"


class MetalUsage(Metal):
    def __init__(self, cpu: int = 0, totalCpu: int = 0,
                 ram: float = 0, totalRam: float = 0,
                 disk: float = 0, totalDisk: float = 0):
        super().__init__(cpu, ram, disk)
        self.TotalCpu = totalCpu
        self.TotalRam = totalRam
        self.TotalDisk = totalDisk

    def __repr__(self):
        return f"C:{self.Cpu}/{self.TotalCpu} R:{self.Ram}/{self.TotalRam} S:{self.Disk}/{self.TotalDisk}"
