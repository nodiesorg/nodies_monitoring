import asyncio
import urllib.parse

from appmetrics.AppMetrics import AppMetrics
from connectors.ChainUrl import ChainUrl
from connectors.EthConnector import EthConnector
from connectors.HttpClient import HttpClient
from data.AvaxChainID import AvaxChainID
from data.ChainSyncStatus import ChainSyncStatus
from data.PoktChainID import PoktChainID


class AvaxConnector(EthConnector):
    """
    This constructor will set the parent constructor's endpoint_uri to end with /ext/bc/C/rpc as a default.
    The chain_url_obj is an extra member in this field because some api calls don't require any suffix.
    Chain is a reference to the blockchain number. For avalanche this is P/C/X. DFKs for example is
    q2aTwKuyzgs8pynF7UXBZCU7DejbZbZ6EUyHr3JQzYgwNPUPi
    """

    def __init__(self, chain_url_obj: ChainUrl, destination: AppMetrics, id: str, chain: str, client_session, request_kwargs=None):
        self.chain_url_obj = chain_url_obj
        self.fqd = ChainUrl(urllib.parse.urljoin(self.chain_url_obj.get_endpoint(), f"/ext/bc/{chain}/rpc"))
        super().__init__(self.fqd, destination, id, request_kwargs)
        self.chain = chain
        self._set_labels()
        self.http_client = HttpClient(client_session)

    def _set_labels(self):
        """
        This method will set the labels ID according to the passed AVAX chain ID:
        """
        if self.chain == AvaxChainID.DFK.value:
            self.labels = [PoktChainID.DFK.value, str(self.chain_url_obj)]
        elif self.chain == AvaxChainID.SWIMMER.value:
            self.labels = [PoktChainID.SWIMMER.value, str(self.chain_url_obj)]
        elif self.chain == "P":
            self.labels = [PoktChainID.AVAXP.value, str(self.chain_url_obj)]
        elif self.chain == "C":
            self.labels = [PoktChainID.AVAXC.value, str(self.chain_url_obj)]
        elif self.chain == "X":
            self.labels = [PoktChainID.AVAXX.value, str(self.chain_url_obj)]
        else:
            self.labels = [self.id, str(self.chain_url_obj)]

    async def get_sync_data(self) -> dict:
        is_bootstrapped = await self.is_bootstrapped()
        sync_dict = {"status": ChainSyncStatus.SYNCED if is_bootstrapped else ChainSyncStatus.SYNCING}
        tasks = [
            asyncio.ensure_future(self.get_current_block()),
            asyncio.ensure_future(self.get_latest_block())
        ]
        curr_height, latest_height, *_ = await asyncio.gather(*tasks)
        sync_dict["current_block"] = curr_height
        sync_dict["latest_block"] = latest_height

        return sync_dict

    async def get_latest_block(self) -> int:

        if self.chain == "X":
            # TODO: Determine how to retrieve X sync data
            return -1

        curr = await self.get_current_block()
        outstanding = await self.get_outstanding_blocks()
        return curr + outstanding

    async def get_current_block(self) -> int:

        if self.chain == "X":
            # TODO: Determine how to retrieve X sync data
            return -1

        if not self.chain == "P":
            return await super().get_current_block()

        endpoint = urllib.parse.urljoin(self.chain_url_obj.get_endpoint(), "/ext/bc/P")
        payload = {
                    "jsonrpc": "2.0",
                    "method": "platform.getHeight",
                    "params": {},
                    "id": 1
                }
        response = self.http_client.post(endpoint, payload)
        return int(response["result"]["height"])

    async def is_bootstrapped(self) -> bool:
        endpoint = urllib.parse.urljoin(self.chain_url_obj.get_endpoint(), "/ext/info")
        payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "info.isBootstrapped",
                    "params": {
                        "chain": self.chain
                    }
                }
        response = self.http_client.post(endpoint, payload)
        return response["result"]["isBootstrapped"]

    async def get_outstanding_blocks(self):
        endpoint = urllib.parse.urljoin(self.chain_url_obj.get_endpoint(), "/ext/health")
        payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "health.health"
                }
        response = self.http_client.post(endpoint, payload)
        return response["result"]["checks"][self.chain]["message"]["consensus"][
                "outstandingBlocks"]
