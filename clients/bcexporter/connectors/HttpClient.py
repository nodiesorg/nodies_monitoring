import aiohttp
import json
from connector_utils import get_http_client

class HttpClient():

    def __init__(self, client_session):
        self.client_session = client_session

    async def post(self, endpoint, payload, headers={"content-type": "application/json"}, timeout=5):
        response = await self.async_session.post(
            timeout=timeout,
            url=endpoint,
            json=payload,
            headers=headers
        )
        json_object = json.loads((await response.content.read()).decode("utf8"))
        return json_object
