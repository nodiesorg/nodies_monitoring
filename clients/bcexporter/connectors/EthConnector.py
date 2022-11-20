import asyncio
import traceback

from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware

from appmetrics.AppMetrics import AppMetrics
from connectors.ChainUrl import ChainUrl
from connectors.Web3Connector import Web3Connector
from data.ChainSyncStatus import ChainSyncStatus


class EthConnector(Web3Connector):

    def __init__(self, chain_url_obj: ChainUrl, destination: AppMetrics, id: str, request_kwargs=None):
        self.id = id
        self.chain_url_obj = chain_url_obj
        self.labels = [id, str(chain_url_obj)]
        self.w3 = Web3(AsyncHTTPProvider(chain_url_obj.get_endpoint(), request_kwargs)
                       , modules={'eth': AsyncEth}
                       , middlewares=[async_geth_poa_middleware])
        self.destination = destination

    async def get_sync_data(self) -> dict:
        # Returns dict if currently syncing, otherwise returns False
        sync_data = await self.w3.eth.syncing
        sync_dict = {}
        # If not currently syncing
        if not sync_data:
            tasks = [
                asyncio.ensure_future(self.get_current_block())
            ]
            curr_height, *_ = await asyncio.gather(*tasks)
            sync_dict["status"] = ChainSyncStatus.SYNCED
            sync_dict["current_block"] = curr_height
            sync_dict["latest_block"] = curr_height
        else:
            sync_dict["status"] = ChainSyncStatus.SYNCING
            sync_dict["current_block"] = sync_data.get("currentBlock", 0)
            sync_dict["latest_block"] = sync_data.get("highestBlock", 0)

        return sync_dict

    async def get_current_block(self) -> int:
        return await self.w3.eth.get_block_number()

    async def get_latest_block(self) -> int:
        """
        Latest block is same as current block whenever node is synced.
        We can later replace this with a value from an explorer or an altruist if needed.
        """
        return await self.get_current_block()

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
            self.destination.sync_status.labels(*self.labels).set(sync_data["status"])
            print(f"{self.chain_url_obj.get_endpoint()} sent metrics for chain {self.id}")
            print(f'Status: {sync_data["status"]}\nCurrent Height: {curr_height}\nLatest Height: {latest_height}')
        except (asyncio.TimeoutError) as e:
            print(f'Timeout Exception with: {self.chain_url_obj.get_endpoint()}')
            traceback.print_exc()
            self.destination.sync_status.labels(*self.labels).set(ChainSyncStatus.STOPPED)
            self.destination.curr_height.labels(*self.labels).set(0)
            self.destination.latest_height.labels(*self.labels).set(0)
        except Exception as e:
            print(f'Exception with: {self.chain_url_obj.get_endpoint()}')
            traceback.print_exc()
            #temporary until graphs can handle UNKNOWN
            self.destination.sync_status.labels(*self.labels).set(ChainSyncStatus.STOPPED)
            self.destination.curr_height.labels(*self.labels).set(0)
            self.destination.latest_height.labels(*self.labels).set(0)
