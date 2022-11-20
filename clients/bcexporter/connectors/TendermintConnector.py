import asyncio
import traceback
from appmetrics.AppMetrics import AppMetrics
from connectors.ChainUrl import ChainUrl
from data.ChainSyncStatus import ChainSyncStatus


class TendermintConnector(Web3Connector):

    def __init__(self, chain_url_obj: ChainUrl, destination: AppMetrics, id: str, request_kwargs=None):
        self.id = id
        self.chain_url_obj = chain_url_obj
        self.labels = [id, str(chain_url_obj)]
        self.destination = destination

    async def get_sync_data(self) -> dict:
        # Returns dict if currently syncing, otherwise returns False
        # TODO: Call Tendermint status endpoint, return sync_info["latest_block_height"] as current and latest block
        # TODO: is syncing = sync_info["catching_up"] (AKA when consensus reactor is firing)
        # TODO: do we even need get_current_block / get_latest_block impl? Or cache it. Otherwise we call /status endpoint twice.
        sync_dict = {}
        return sync_dict

    async def get_current_block(self) -> int:
        return -1

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
