from REST import RestClient, Payload
from datetime import datetime, timezone
from Settings import NefEmulator as Config
from enum import Enum, unique


@unique
class Loop(Enum):
    Stop = 0
    Start = 1


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
        status, success = self.ResponseStatusCode(response)

        if not success:
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

    def ToggleLoop(self, supi: str, action: Loop) -> str:
        """Returns the received string on success, otherwise raises an exception"""
        headers = self.getExtraHeaders()
        url = f"/api/v1/ue_movement/{('start' if action == Loop.Start else 'stop')}-loop/"
        payload = {'supi': supi}

        try:
            response = self.HttpPost(url, payload=Payload.Data, body=payload, extra_headers=headers)
            status, success = self.ResponseStatusCode(response)
            data = self.ResponseToJson(response)

            if success:
                return data['msg']
            else:
                msg = data.get('msg', data.get('detail', str(data)))
                raise RuntimeError(msg)
        except Exception as e:
            raise RuntimeError(f"Unable to {action.name.lower()} loop for supi '{supi}': {e}") from e
