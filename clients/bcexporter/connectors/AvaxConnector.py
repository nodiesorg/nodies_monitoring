import asyncio
import json
import urllib.parse

import aiohttp

from connectors.EthConnector import EthConnector
from data.AvaxChainID import AvaxChainID
from data.PoktChainID import PoktChainID


class AvaxConnector(EthConnector):
    """
    This constructor will set the parent constructor's endpoint_uri to end with /ext/bc/C/rpc as a default.
    The base_url is an extra member in this field because some api calls don't require any suffix.
    Chain is a reference to the blockchain number. For avalanche this is P/C/X. DFKs for example is
    q2aTwKuyzgs8pynF7UXBZCU7DejbZbZ6EUyHr3JQzYgwNPUPi
    """

    def __init__(self, endpoint_uri, destination, id, chain, request_kwargs=None):
        self.base_url = endpoint_uri
        self.fqd = urllib.parse.urljoin(self.base_url, f"/ext/bc/{chain}/rpc")
        super().__init__(self.fqd, destination, id, request_kwargs)
        self.chain = chain
        self._set_labels()

    def _set_labels(self):
        """
        This method will set the labels ID according to the passed AVAX chain ID:
        """
        if self.chain == AvaxChainID.DFK.value:
            self.labels = [PoktChainID.DFK.value, self.base_url]
        elif self.chain == AvaxChainID.SWIMMER.value:
            self.labels = [PoktChainID.SWIMMER.value, self.base_url]
        elif self.chain == "P":
            self.labels = [PoktChainID.AVAXP.value, self.base_url]
        elif self.chain == "C":
            self.labels = [PoktChainID.AVAXC.value, self.base_url]
        elif self.chain == "X":
            self.labels = [PoktChainID.AVAXX.value, self.base_url]
        else:
            self.labels = [self.id, self.base_url]

    async def get_sync_data(self):
        sync_data = await self.is_bootstrapped()
        sync_dict = {}
        if not sync_data:
            sync_dict["status"] = "syncing"
        else:
            sync_dict["status"] = "synced"
        if not self.chain == "X":
            tasks = [
                asyncio.ensure_future(self.get_current_block()),
                asyncio.ensure_future(self.get_latest_block())
            ]
            curr_height, latest_height, *_ = await asyncio.gather(*tasks)
            sync_dict["current_block"] = curr_height
            sync_dict["latest_block"] = latest_height
        return sync_dict

    async def get_latest_block(self):
        curr = await self.get_current_block()
        outstanding = await self.get_outstanding_blocks()
        return curr + outstanding

    async def get_current_block(self):
        if not self.chain == "P":
            return await super().get_current_block()
        else:
            async with aiohttp.ClientSession() as async_session:
                endpoint = urllib.parse.urljoin(self.base_url, "/ext/bc/P")
                response = await async_session.post(
                    url=endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "method": "platform.getHeight",
                        "params": {},
                        "id": 1
                    },
                    headers={"content-type": "application/json"}
                )
                json_object = json.loads((await response.content.read()).decode("utf8"))
                return int(json_object["result"]["height"])

    async def is_bootstrapped(self):
        endpoint = urllib.parse.urljoin(self.base_url, "/ext/info")
        async with aiohttp.ClientSession() as async_session:
            response = await async_session.post(
                url=endpoint,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "info.isBootstrapped",
                    "params": {
                        "chain": self.chain
                    }
                },
                headers={"content-type": "application/json"}
            )
            json_object = json.loads((await response.content.read()).decode("utf8"))
        return json_object["result"]["isBootstrapped"]

    async def get_outstanding_blocks(self):
        endpoint = urllib.parse.urljoin(self.base_url, "/ext/health")
        async with aiohttp.ClientSession() as async_session:
            response = await async_session.post(
                url=endpoint,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "health.health"
                },
                headers={"content-type": "application/json"}
            )
            json_object = json.loads((await response.content.read()).decode("utf8"))
        if self.chain == AvaxChainID.DFK:  # DFK
            response_json = \
                json_object["result"]["checks"][AvaxChainID.DFK]["message"][
                    "consensus"]["outstandingBlocks"]
        elif self.chain == AvaxChainID.SWIMMER:  # Swimmer
            response_json = \
                json_object["result"]["checks"][AvaxChainID.SWIMMER]["message"][
                    "consensus"]["outstandingBlocks"]
        elif self.chain == "P":
            response_json = json_object["result"]["checks"]["P"]["message"]["consensus"][
                "outstandingBlocks"]
        else:  # C chain
            response_json = json_object["result"]["checks"]["C"]["message"]["consensus"][
                "outstandingBlocks"]
        return response_json

    async def report_metrics(self):
        """
          Get metrics from node and refresh Prometheus metrics with
          new values.
          """
        print(self.chain)
        if self.chain == "X":
            try:
                sync_data = await self.get_sync_data()
            except ConnectionError:
                print(f"Could not connect to {self.endpoint_uri}")
            except Exception as e:
                print(f'Exception with: {self.base_url}')
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(e).__name__, e.args)
                print(message)
            except (ConnectionError, Exception):
                self.destination.sync_status.labels(*self.labels).set(-1)
            else:
                if sync_data["status"] == "syncing":
                    self.destination.sync_status.labels(*self.labels).set(0)
                else:
                    self.destination.sync_status.labels(*self.labels).set(1)
                print(f"{self.endpoint_uri} sent metrics for chain {self.id}")
                print(f'Status: {sync_data["status"]}')
        else:
            await super().report_metrics()
