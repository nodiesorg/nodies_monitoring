from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.monitoring import Prometheus
from diagrams.onprem.logging import Loki
from diagrams.saas.chat import Slack
from diagrams.onprem.container import Docker

with Diagram("Nodies Monitoring", filename="architecture", show=False):
    with Cluster("Client"):
        # definitions
        blockchain_exporter = Docker("Blockchain Exporter")
        node_exporter = Docker("Node Exporter")
        cadvisor = Docker("CAdvisor")
        promtail = Docker("Promtail")

        # connections

    with Cluster("Server"):
        # definitions
        grafana = Grafana("Grafana")
        minio = Custom("Minio", "./MINIO_Bird.png")

        with Cluster("Datasources"):
            # definitions
            prometheus = Prometheus("Prometheus")
            loki = Loki("Loki")

        # connections
        prometheus << Edge(label='query', color="black", style="solid") << grafana
        loki << Edge(label='query', color="black", style="solid") << grafana
        loki >> Edge(label='store', color="black", style="solid") >> minio
        loki >> Edge(label='query', color="black", style="solid") >> minio

    # definitions
    slack = Slack("Slack")

    # connections
    blockchain_exporter << Edge(label='scrape', color="black", style="solid") << prometheus
    node_exporter << Edge(label='scrape', color="black", style="solid") << prometheus
    cadvisor << Edge(label='scrape', color="black", style="solid") << prometheus
    promtail >> Edge(label='push', color="black", style="solid") >> loki
    grafana >> Edge(label='alert', color="red", style="solid") >> slack