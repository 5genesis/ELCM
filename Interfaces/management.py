from REST import RestClient
from Helper import Config, Log
from typing import Dict, Optional, Tuple, List
from Data import Metal, MetalUsage, NsInfo
from Facility import Facility


class Management:
    sliceManager = None

    @classmethod
    def HasResources(cls, owner: 'ExecutorBase', localResources: List[str],
                     networkServices: List[NsInfo], exclusive: bool) -> Tuple[bool, bool]:
        """Returns [<available>, <feasible>].
            - Available indicates that the required local resources are locked and can be used, and there are
            enough on all VIMs to fit the network services.
            - A feasible value of False indicates that the network services can never fit on the VIMs due to
            their total resoutces.
            """

        if len(networkServices) != 0:
            try:
                vimResources = cls.SliceManager().GetVimResources()
            except Exception as e:
                Log.E(f"Exception while retrieving VIM resources: {e}")
                return False, True

            totalRequired: Dict[str, Metal] = {}
            for ns in networkServices:
                vim = ns.Location
                if vim not in totalRequired.keys():
                    totalRequired[vim] = Metal(0, 0, 0)
                totalRequired[vim] += ns.Requirements
            Log.D(f"Total requirements from each VIM: {totalRequired}")

            for vim, required in totalRequired.items():
                if vim not in vimResources.keys():
                    Log.E(f"Unknown VIM {vim}. Execution unfeasible.")
                    return False, False
                current = vimResources[vim]
                if (required.Cpu > current.TotalCpu or
                        required.Ram > current.TotalRam or required.Disk > current.TotalDisk):
                    Log.E(f"Insufficient resources on {vim}. Execution unfeasible ({required} > {current})")
                    return False, False
                if required.Cpu > current.Cpu or required.Ram > current.Ram or required.Disk > current.Disk:
                    return False, True  # Execution possible, but not enough resources at the moment

        return Facility.TryLockResources(localResources, owner, exclusive), True

    @classmethod
    def ReleaseLocalResources(cls, owner: 'ExecutorBase', localResources: List[str]):
        Facility.ReleaseResources(localResources, owner)

    @classmethod
    def SliceManager(cls):
        if cls.sliceManager is None:
            settings = Config().SliceManager
            cls.sliceManager = SliceManager(settings.Host, settings.Port)
        return cls.sliceManager


class SliceManager(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, "/api")

    def CreateSlice(self, nsd: str) -> Tuple[str, bool]:
        response = self.HttpPost(f"{self.api_url}/slice", {"Content-Type": "application/json"}, nsd)
        status = self.ResponseStatusCode(response)
        if status in [201, 400]:  # Responses with textual information
            return response.data.decode('utf-8'), (status == 201)
        else:
            return f"Unable to create slice: Status {status} ({response.reason})", False

    def CheckSlice(self, slice: str) -> Optional[Dict]:
        response = self.HttpGet(f"{self.api_url}/slice/{slice}", {"Accept": "application/json"})
        return None if self.ResponseStatusCode(response) == 404 else self.ResponseToJson(response)

    def SliceCreationTime(self, slice: str) -> Dict:
        response = self.HttpGet(f"{self.api_url}/slice/{slice}/time", {"Accept": "application/json"})
        return self.ResponseToJson(response)

    def DeleteSlice(self, slice: str) -> Tuple[str, bool]:
        response = self.HttpDelete(f"{self.api_url}/slice/{slice}")
        status = self.ResponseStatusCode(response)
        if status == 200:
            return response.data.decode('utf-8'), True
        else:
            return f"Unable to delete slice: Status {status} ({response.reason})", False

    def GetVimResources(self) -> Dict[str, MetalUsage]:
        response = self.HttpGet(f"{self.api_url}/resources")
        status = self.ResponseStatusCode(response)
        res = {}
        if status == 200:
            data = self.ResponseToJson(response)
            try:
                for vim in data["VIMs"]:
                    name = vim["name"]
                    total = vim["max_resources"]
                    current = vim["available_resources"]
                    metal = MetalUsage(cpu=current['CPUs'], ram=current['RAM'], disk=current['Disk'],
                                       totalCpu=total['CPUs'], totalRam=total['RAM'], totalDisk=total['Disk'])
                    res[name] = metal
            except Exception as e:
                Log.E(f"Exception while retrieving VIM resources: {e}")
                Log.D(f"Payload: {data}")
        return {'Edge': MetalUsage(4, 4, 8192, 8192, 80, 80)}

    def GetNsdInfo(self, nsd: str = None) -> Dict:
        url = f"{self.api_url}/nslist{('' if nsd is None else f'?nsd-id={nsd}')}"
        response = self.HttpGet(url, {"Accept": "application/json"})
        return self.ResponseToJson(response)

    def GetNsdRequirements(self, nsd: str) -> Optional[Metal]:
        try:
            data = self.GetNsdInfo(nsd)
            if isinstance(data, list):
                if len(data) != 0:
                    data = data[0]
                else: raise RuntimeError("Received an empty list")
            try:
                flavor = data["flavor"]
                return Metal(cpu=flavor["vcpu-count"], ram=flavor["memory-mb"], disk=flavor["storage-gb"])
            except KeyError as k:
                raise RuntimeError(f"'{k}' key not present in data")
        except Exception as e:
            Log.E(f"Exception while retrieving NSD information: {e}")
            return None

    def GetBaseSliceDescriptors(self) -> List[str]:
        url = f"{self.api_url}/base_slice_des"
        response = self.HttpGet(url, {"Accept": "application/json"})
        data: List[Dict] = self.ResponseToJson(response)
        return [desc['Slice_des_ID'] for desc in data]


