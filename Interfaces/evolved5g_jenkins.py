from REST import RestClient, Payload
from typing import List, Tuple, Dict, Optional
from Helper import Log
from datetime import datetime, timezone


class Evolved5gJenkinsApi(RestClient):
    EXPIRY_MARGIN = 60

    def __init__(self, host, port, user, password):
        super().__init__(host, port, '', https=True, insecure=False)
        self.basicAuth = {"username": user, "password": password}
        self.token = None
        self.expiry = 0

    def RenewToken(self):
        response = self.HttpPost("/api/auth", payload=Payload.Data, body=self.basicAuth)
        status = self.ResponseStatusCode(response)

        if status != 200:
            raise RuntimeError(f"Unexpected status {status} retrieving token: {self.ResponseToRaw(response)}")
        try:
            data = self.ResponseToJson(response)
            self.token = data['access_token']
            delay = float(data['expires_in'])
            if delay >= self.EXPIRY_MARGIN:
                delay = delay - self.EXPIRY_MARGIN
            self.expiry = datetime.now(timezone.utc).timestamp() + delay
        except Exception as e:
            raise RuntimeError(f'Could not extract token information: {e}') from e

    def MaybeRenewToken(self):
        current = datetime.now(timezone.utc).timestamp()
        if self.token is None or current >= self.expiry:
            self.RenewToken()

    def TriggerBuild(self):
        pass

    def CheckStatus(self):
        pass
