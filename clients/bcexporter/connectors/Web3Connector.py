from abc import ABC, abstractmethod

from appmetrics import AppMetrics


class Web3Connector(ABC):
    """
    Endpoint_uri should be the full URI to the RPC endpoint such as https://localhost:8545
    For RPC servers behind HTTP connections running on port 80 and HTTPS
    Connections running on port 443 the port can be omitted from the URI.

    Request_kwargs should be a dictionary of keyword arguments which
    will be passed onto each http/https POST request made to your node.

    Session allows you to pass a requests. Session object initialized as desired.
    """

    @abstractmethod
    def __init__(self, endpoint_uri, destination: AppMetrics, request_kwargs=None, session=None):
        pass

    @abstractmethod
    def get_current_block(self):
        pass

    @abstractmethod
    def get_latest_block(self):
        pass

    @abstractmethod
    def report_metrics(self):
        pass
