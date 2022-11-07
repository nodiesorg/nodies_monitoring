from appmetrics.AppMetrics import AppMetrics
from connectors.AvaxConnector import AvaxConnector
from connectors.EthConnector import EthConnector
from data.AvaxChainID import AvaxChainID
from data.PoktChainID import PoktChainID


def create_connectors(appmetrics: AppMetrics, chains):
    connectors = []
    for chain in chains:
        if chain["id"] == PoktChainID.SWIMMER:
            connectors.append(AvaxConnector(endpoint_uri=chain["url"], destination=appmetrics, id=chain["id"],
                                            chain=AvaxChainID.SWIMMER))

        elif chain["id"] == PoktChainID.AVAX:
            [connectors.append(
                AvaxConnector(endpoint_uri=chain["url"], destination=appmetrics, id=chain["id"], chain=subnet))
                for subnet in ["P", "X", "C"]]

        elif chain["id"] == PoktChainID.DFK:
            connectors.append(AvaxConnector(endpoint_uri=chain["url"], destination=appmetrics, id=chain["id"],
                                            chain=AvaxChainID.DFK))
        else:
            connectors.append(EthConnector(endpoint_uri=chain["url"], destination=appmetrics, id=chain["id"]))

    return connectors
