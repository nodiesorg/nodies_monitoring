import asyncio

from appmetrics.AppMetrics import AppMetrics
from appmetrics.AppMetricsServer import AppMetricsServer
from config.Config import Config


async def main():
    config = Config()
    metrics = AppMetrics()
    server = AppMetricsServer(config=config, appmetrics=metrics)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
