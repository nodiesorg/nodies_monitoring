import asyncio

from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware

from connectors.Web3Connector import Web3Connector
from data.ChainSyncStatus import ChainSyncStatus


class EthConnector(Web3Connector):

    def __init__(self, endpoint_uri, destination, id, request_kwargs=None):
        self.id = id
        self.endpoint_uri = endpoint_uri
        self.labels = [id, endpoint_uri]
        self.w3 = Web3(AsyncHTTPProvider(endpoint_uri, request_kwargs)
                       , modules={'eth': AsyncEth}
                       , middlewares=[async_geth_poa_middleware])
        self.destination = destination

    async def get_sync_data(self):
        # Returns dict if currently syncing, otherwise returns False
        sync_data = await self.w3.eth.syncing
        sync_dict = {}
        # If not currently syncing
        if not sync_data:
            tasks = [
                asyncio.ensure_future(self.get_current_block()),
                asyncio.ensure_future(self.get_latest_block())
            ]
            curr_height, latest_height, *_ = await asyncio.gather(*tasks)
            sync_dict["status"] = ChainSyncStatus.SYNCED
            sync_dict["current_block"] = curr_height
            sync_dict["latest_block"] = latest_height
        else:
            sync_dict["status"] = ChainSyncStatus.SYNCING
            sync_dict["current_block"] = sync_data["currentBlock"]
            sync_dict["latest_block"] = sync_data["latestBlock"]
        return sync_dict

    async def get_current_block(self):
        return await self.w3.eth.get_block_number()

    async def get_latest_block(self):
        return (await self.w3.eth.get_block("latest"))["number"]

    async def report_metrics(self):
        """
        Get metrics from node and refresh Prometheus metrics with
        new values.
        """
        try:
            sync_data = await self.get_sync_data()
            curr_height = sync_data["current_block"]
            latest_height = sync_data["latest_block"]
            self.destination.curr_height.labels(*self.labels).set(curr_height)
            self.destination.latest_height.labels(*self.labels).set(latest_height)
            print(f"{self.endpoint_uri} sent metrics for chain {self.id}")
            print(f'Status: {sync_data["status"]}\nCurrent Height: {curr_height}\nLatest Height: {latest_height}')
        except ConnectionError:
            print(f"Could not connect to {self.endpoint_uri}")
        except Exception as e:
            print(f'Exception with: {self.endpoint_uri}')
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
        except (ConnectionError, Exception):
            self.destination.sync_status.labels(*self.labels).set(ChainSyncStatus.STOPPED)
        else:
            self.destination.sync_status.labels(*self.labels).set(sync_data["status"])
