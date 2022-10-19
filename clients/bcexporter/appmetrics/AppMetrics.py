from prometheus_client import Gauge


class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self):
        self.sync_status = Gauge("sync_state", "State of syncing", labelnames=["blockchain_id", "endpoint"])
        self.curr_height = Gauge('current_height', 'The blockchain node\'s current height',
                                 labelnames=["blockchain_id", "endpoint"])
        self.latest_height = Gauge('latest_height', 'The blockchain node\'s latest height',
                                   labelnames=["blockchain_id", "endpoint"])
