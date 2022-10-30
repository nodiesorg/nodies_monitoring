### [README still WIP, not contribution friendly yet]

Nodies Monitoring is a customizable and extensible monitoring solution for monitoring host machine metrics, container metrics, node status and node logs. 

## Table of content

- [Installation](#installation)
    - [Docker Dependencies](#docker-dependencies)
    - [Nodies Monitoring](#nodies-monitoring)
- [Setup](#setup)
    - [chains.json](#chainsjson)
    - [.env](#env)
    - [Promtail Logs](#promtail-logs)
    - [Yaml Setup and Startup](#yaml-setup-and-startup)
- [Examples](#examples)
    - [Datasources](#datasources)
    - [Dashboards](#dashboards)
    - [Alerts](#alerts)
- [License](#license)
- [Links/Contact](#linkscontact)

## Installation

**Note:** Tested and recommended installation on Ubuntu 22.04.1 LTS host OS

### Docker Dependencies
<details>
<summary>Optional section for fresh install</summary>

Uninstall existing docker
```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

Install required packages
```bash
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

Add docker official GPG key
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

Setup docker repo
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Update apt package index
```bash
sudo apt-get update
```

Install latest docker
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```
</details>

### Nodies Monitoring

Git pulldown nodies monitoring project
```bash
git clone --branch main https://YuppiePF@github.com/baaspoolsllc/nodies_monitoring.git
```

Install python3-pip
```bash
apt install python3-pip
```

Install requirements
```bash
pip3 install -r requirements.txt
```

## Setup

### chains.json

<details>
<summary>Supported Blockchains</summary>

- harmony
- polygon
- xdai
- eth
- bsc
- swimmer
- avax
- dfk
- other EVM chains should work but not tested
</details>

Copy your chains.json to [./clients/bcexporter/config](clients/bcexporter/config/)

### .env

Create a .env file in the root [nodies_monitoring](./) folder

```
MONITORING_ENDPOINT=111.222.333.001
EXPORTER_ENDPOINT=111.222.333.002
SLACK_WEBHOOK=https://hooks.slack.com/services/your_slack_webhook_string

LOKI_PORT=3100
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
MINIO_PORT=9000
ALERTMANAGER_PORT=9093

BLOCKCHAIN_EXPORTER_PORT=9877
NODE_EXPORTER_PORT=9100
CADVISOR_EXPORTER_PORT=8080
PROMTAIL_PORT=9080
```

- Update MONITORING_ENDPOINT with the ip address of the host that will run the [monitoring stack](./server) (loki, grafana, minio, prometheus, alertmanager)

- Update EXPORTER_ENDPOINT with the ip address of the host that will run any services of the [exporter_stack](./clients) (blockchain_exporter, cadvisor, node_exporter, promtail)

- Update SLACK_WEBHOOK with the webhook of the slack channel to send grafana-managed alerts to

### Promtail Logs

**Note:** Logs are expected by default to be located in [./clients/log/](./clients/log)

### Yaml Setup and Startup

<details>
<summary>Monitoring</summary>

SSH into your monitoring host

Change directory into the [server](./server) subfolder, and run [setup.py](./server/setup.py)
```bash
cd nodies_monitoring/server && python3 setup.py
```

Boot up all server services
```bash
docker compose up
```
</details>

<details>
<summary>Exporter</summary>

SSH into your exporter host

Change directory into the [clients](./clients) subfolder, and run [setup.py](./clients/setup.py)

```bash
cd nodies_monitoring/clients && python3 setup.py
```

Boot up all server services
```bash
docker compose up
```
</details>

## Examples

### Datasources

Default datasources have been provisioned in [./templates/datasources](./templates/datasources)

To add additional datasources, please refer to [grafana datasource documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/#data-sources)

### Dashboards

Default dashboards have been provisioned in [./server/grafana/dashboards](./server/grafana/dashboards)

To add additional dashboards, please refer to [grafana dashboard documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)

#### Chain Metrics

![Chain Metrics](./img/chain_metrics.png)

#### Pokt Log

*Image goes here*

#### Machine Metrics

![Machine Metrics](./img/machine_metrics.png)

#### Container Metrics

![Container Metrics](./img/container_metrics.png)

### Alerts

Default alerting has been provisioned in [./server/grafana_provisioning/alerting](./server/grafana_provisioning/alerting)

To add additional alerting, please refer to [grafana alerting documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/#alerting)

## License

The nodies monitoring project is licensed under the terms of the *LICENSE GOES HERE*.

## Links/Contact

For any inquiries, please reach out to PoktBlade(PoktBlade#5970) or poktdachi(dachi#0005) on the pokt discord

[![](https://dcbadge.vercel.app/api/server/pokt)](https://discord.gg/pokt)