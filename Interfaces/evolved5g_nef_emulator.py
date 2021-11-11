from REST import RestClient, Payload
from datetime import datetime, timezone
from Settings import NefEmulator as Config


class Evolved5gNefEmulator(RestClient):
    EXPIRY_TIME = 60*60*24*8  # Current configuration is 8 days

    def __init__(self, config: Config):
        super().__init__(config.Host, config.Port, '')
        self.authPayload = {
            'grant_type': 'password',
            'username': config.User,
            'password': config.Password,
            'client_id': '',
            'client_secret': ''
        }
        self.token = None
        self.expiry = 0

    def RenewToken(self):
        response = self.HttpPost("/api/v1/login/access-token", payload=Payload.Form, body=self.authPayload)
        status = self.ResponseStatusCode(response)

        if status != 200:
            raise RuntimeError(f"Unexpected status {status} retrieving token: {self.ResponseToRaw(response)}")
        try:
            data = self.ResponseToJson(response)
            self.token = data['access_token']
            self.expiry = datetime.now(timezone.utc).timestamp() + self.EXPIRY_TIME - 60  # 1 minute margin
        except Exception as e:
            raise RuntimeError(f'Could not extract token information: {e}') from e

    def MaybeRenewToken(self):
        current = datetime.now(timezone.utc).timestamp()
        if self.token is None or current >= self.expiry:
            self.RenewToken()

    def getExtraHeaders(self):
        self.MaybeRenewToken()
        return {"Content-Type": "application/json",
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}"}
