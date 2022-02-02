from Task import Task
from Helper import Level
from REST import RestClient, Payload


class RestApi(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("REST API", parent, params, logMethod, None)
        self.paramRules = {
            'Host': (None, True),
            'Port': (None, True),
            'Endpoint': (None, True),
            'Https': (False, False),
            'Insecure': (False, False),
            'Method': ('GET', False),
            'Payload': ('{}', False),
            'PayloadMode': (None, False),
            'Responses': (None, False),
            'Timeout': (10, False),
            'Headers': (None, False)
        }

    def Run(self):
        client = RestClient(self.params['Host'], self.params['Port'], "",
                            self.params['Https'], self.params['Insecure'])

        endpoint = self.params['Endpoint']
        method = str(self.params['Method']).upper()
        payload = self.params['Payload']
        payloadMode = self.params['PayloadMode']
        timeout = self.params['Timeout']
        headers = self.params['Headers']
        statusCodes = self.params['Responses']

        if statusCodes is not None:
            if not isinstance(statusCodes, (tuple, list)):
                statusCodes = [statusCodes]

            if "Success" in statusCodes:
                statusCodes.remove("Success")
                statusCodes.extend([*range(200, 300)])

        self.Log(Level.INFO, f"Sending '{method}' request to '{client.api_url}', endpoint '{endpoint}'.")
        self.Log(Level.DEBUG, f"Timeout: {timeout}; Extra Headers: {headers}")
        self.Log(Level.DEBUG, f"Payload: {payload}")
        if statusCodes is not None:
            self.Log(Level.DEBUG, f"Accepted status codes: {statusCodes}")

        match method:
            case "GET":
                response = client.HttpGet(endpoint, extra_headers=headers, timeout=timeout)
            case "POST":
                payloadMode = None if payloadMode is None else Payload[payloadMode]
                response = client.HttpPost(endpoint, extra_headers=headers,
                                           body=payload, payload=payloadMode, timeout=timeout)
            case "PATCH":
                response = client.HttpPatch(endpoint, extra_headers=headers, body=payload, timeout=timeout)
            case "DELETE":
                response = client.HttpDelete(endpoint, extra_headers=headers, timeout=timeout)
            case _:
                self.Log(Level.ERROR, f"Unsupported method '{method}'")
                return

        status, _ = client.ResponseStatusCode(response)
        try:
            data = client.ResponseToJson(response)
        except RuntimeError:
            try:
                data = client.ResponseToRaw(response)
            except RuntimeError:
                data = None

        self.Log(Level.INFO, f"Status '{status}'; Response: '{data}'")
        if statusCodes is not None:
            if status not in statusCodes:
                message = f"Unexpected status code received: {status}"
                self.Log(Level.ERROR, message)
                self.MaybeSetErrorVerdict()
                raise RuntimeError(message)
