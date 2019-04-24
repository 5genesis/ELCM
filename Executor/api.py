from REST import RestClient


class Api(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/api/executor')

    def NotifyStart(self, executor_id):
        url = f"{self.api_url}/{executor_id}/start"
        self.httpPost(url)

    def NotifyStop(self, executor_id):
        url = f"{self.api_url}/{executor_id}/stop"
        self.httpPost(url)
