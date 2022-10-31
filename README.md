### [README still WIP, not contribution friendly yet]

Nodies Monitoring is a customizable and extensible monitoring solution for monitoring host machine metrics, container metrics, node status and node logs. 

Our project is split into a server(monitoring) stack, and a client(exporter) stack.

Please see [architecture documentation](./architecture.md) for more details.

Pokt Log Monitoring            |  Chain Monitoring
:-------------------------:|:-------------------------:
![Pokt Log](documentation/dashboards/pokt_log.png)  |  ![Chain Metrics](documentation/dashboards/chain_metrics.png)



## Table of content

- [Installation](#installation)
    - [Dependencies](#dependencies)
    - [Nodies Monitoring](#nodies-monitoring)
- [Getting started](#getting-started)
    - [.env](#env)
    - [Server Setup](#server-setup)
    - [Client Setup](#client-setup)
    - [Supported Chains](#supported-chains)
    - [Run Individual Clients](#run-individual-clients)
- [Customization](#customization)
    - [Datasources](#datasources)
    - [Dashboards](#dashboards)
    - [Alerts](#alerts)
- [License](#license)
- [Links/Contact](#linkscontact)

## Installation

**NOTE:** These dependencies are required on both the server and client stack.

**Note:** Tested and recommended installation on Ubuntu 22.04.1 LTS host OS

### Dependencies

<details>
<summary>Python</summary>

<a href="https://www.python.org/downloads/release/python-3106/">Python 3.10.6</a>

</details>

<details>
<summary>Docker</summary>

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
git clone --branch main https://github.com/baaspoolsllc/nodies_monitoring.git
```

Install python3-pip
```bash
apt install python3-pip
```

Install requirements
```bash
pip3 install -r requirements.txt
```

## Getting Started

### .env

**NOTE:** This step is required on both the server and the client stack.

Modify values for the included template [.env.template](./templates/.env.template) file

- Update SERVER_ENDPOINT with the ip address of the host that will run the [monitoring stack](./server) (loki, grafana, minio, prometheus, alertmanager)

- Update CLIENT_ENDPOINT with the ip address of the host that will run any services of the [exporter_stack](./clients) (blockchain_exporter, cadvisor, node_exporter, promtail)

- Update SLACK_WEBHOOK with the webhook of the slack channel to send grafana-managed alerts to



### Server setup 

- SSH into your server host

- Change directory into the [server](./server) subfolder, and run [setup.py](./server/setup.py)
```bash
cd nodies_monitoring/server && python3 setup.py
```

- Boot up all server services
```bash
docker compose up
```

### Client setup

1. SSH into your client host

2.  Modify values for the included [chains.example.json](./templates/chains.example.json). 


**Note:** Logs are expected by default to be located in [./clients/log/](./clients/log)

3. Change directory into the [clients](./clients) subfolder, and run [setup.py](./clients/setup.py)

```bash
cd nodies_monitoring/clients && python3 setup.py
```


4. Boot up all client services
```bash
docker compose up
```
</details>

## Supported Chains
- harmony
- polygon
- xdai
- eth
- bsc
- swimmer
- avax
- dfk
- other evms should work but not tested```

## Run individual clients
 [setup.py](./clients/setup.py) has an optional CLI flag that allows specific clients to be ran.

- `--clients`
  - Allows control over which clients are ran on the exporter stack
  - Services available:
    - blockchain_exporter
    - promtail
    - cadvisor
    - node_exporter

## Customization

### Datasources

Default datasources have been provisioned in [./templates/datasources](./templates/datasources)

To add additional datasources, please refer to [grafana datasource documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/#data-sources)

### Dashboards

Default dashboards have been provisioned in [./server/grafana/dashboards](./server/grafana/dashboards)

To add additional dashboards, please refer to [grafana dashboard documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)

#### Pokt Log

![Pokt Log](documentation/dashboards/pokt_log.png)


#### Chain Metrics

![Chain Metrics](documentation/dashboards/chain_metrics.png)


#### Machine Metrics

![Machine Metrics](documentation/dashboards/machine_metrics.png)

#### Container Metrics

![Container Metrics](documentation/dashboards/container_metrics.png)

### Alerts

Default alerting has been provisioned in [./server/grafana_provisioning/alerting](./server/grafana_provisioning/alerting)

To add additional alerting, please refer to [grafana alerting documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/#alerting)

## License

The nodies monitoring project is licensed under the terms of the *LICENSE GOES HERE*.

## Links/Contact

For any inquiries, please reach out to PoktBlade(PoktBlade#5970) or poktdachi(dachi#0005) on the pokt discord

[![](https://dcbadge.vercel.app/api/server/pokt)](https://discord.gg/pokt)