
### Monitoring Server Configuration
In `prometheus/prometheus.yml`, add hosts emitting metrics to the targets under scrape config's node job.


### Start Monitoring Server
Run `docker compose up` in root folder.


### Clients/Exporters Configuration

- Promtail


In `clients/docker-compose.yml` under the promtail service configuration, edit `- ./log:/var/log` to the location of your nginx logs.


In promtail/promtail-config.yml, edit clients.url to fit your monitoring server's hostname.

- BCExporter


Add your chains.json to `clients/BCExporter/config/`. Check the readme for supported chains.


Configure your polling rate at `CExporter/config/config.yml`

### Start clients

Now run `docker compose up` in clients root folder.

