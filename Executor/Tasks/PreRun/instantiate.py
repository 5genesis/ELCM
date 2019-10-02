from Task import Task
from Helper import Level, Config
from Interfaces import Management, PortalApi


class Instantiate(Task):
    def __init__(self, logMethod, tempFolder, params):
        super().__init__("Instantiate", params, logMethod, None)
        self.tempFolder = tempFolder

    def Run(self):
        hasNsd = self.params['HasNsd']
        experimentId = self.params['ExperimentId']
        sliceId = None

        if hasNsd:
            self.Log(Level.INFO, f"Downloading NSD file for experiment {experimentId}")
            nsdContent = self.getNsdContent(experimentId)
            self.Log(Level.INFO, 'Contents received. Requesting resources to MANO layer')

            try:
                sliceId = Management.SliceManager().Create(nsdContent)
                self.Log(Level.INFO, f'Slice instantiated, id: {sliceId}.')
            except Exception as e:
                raise Exception(f'Exception while creating slice: {e}') from e
        else:
            self.Log(Level.INFO, 'Instantiation not required, no NSD defined.')

        self.Log(Level.INFO, 'Instantiation completed')
        self.params["SliceId"] = sliceId

    def getNsdContent(self, experimentId):
        try:
            config = Config().Dispatcher
            portal = PortalApi(config.Host, config.Port)
            nsdFile = portal.DownloadNsd(experimentId, self.tempFolder)
            with open(nsdFile, 'r', encoding='utf-8') as file:
                nsdContent = file.read()
            return nsdContent
        except Exception as e:
            raise Exception(f'Exception while downloading NDS file: {e}') from e
