import asyncio
from time import sleep

from prometheus_client import start_http_server

from connectors.connector_utils import create_connectors


class AppMetricsServer:

    def __init__(self, config, appmetrics):
        self.config = config
        self.appmetrics = appmetrics
        self.connectors = create_connectors(self.appmetrics, self.config.chains)

    def __str__(self):
        text = ''
        for connector in self.config.connectors:
            text += f"Id={connector.id}\tURL={connector.endpoint_uri}\n"
        return f"""AppMetricsServer has below chains\n{text}"""

    async def start(self):
        start_http_server(self.config.exporter_port)
        """Metrics fetching"""
        while True:
            tasks = []
            for connector in self.connectors:
                tasks.append(
                    asyncio.ensure_future(connector.report_metrics())
                )
            _results = await asyncio.gather(*tasks)
            print(f"Sleeping for {self.config.polling_interval_seconds}")
            sleep(self.config.polling_interval_seconds)
