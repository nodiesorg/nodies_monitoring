import yaml
import os

run_prometheus = False
run_loki = False
run_provisoning_datasources = False
run_contactpoint = False
run_client_promtail = False
run_client_bcexporter = False
run_docker_compose = False

template_prometheus = './templates/prometheus.yml'
output_prometheus = './prometheus/prometheus.yml'

template_loki = './templates/loki-config.yml'
output_loki = './loki/loki-config.yml'

template_datasource = './templates/datasources'
output_datasource = './grafana_provisioning/datasources'

template_contactpoint = './alerting/contactpoint.yaml'
output_contactpoint = './grafana_provisioning/alerting/contactpoint.yaml'

template_client_promtail = './temlpates/clients/promtail-config.yml'
output_client_promtail = './clients/promtail/promtail-config.yml'

template_client_bcexporter = './templates/clients/config.yml'
output_client_bcexporter = './clients/bcexporter/config/config.yml'

template_docker_compose = './docker-compose.yml'
output_docker_compose = './docker-compose.yml'

if run_prometheus:
    with open(template_prometheus, "r") as f:
        newdict = yaml.safe_load(f)
    list_scrape_configs = newdict["scrape_configs"]
    for idx, scrape_config in enumerate(list_scrape_configs):
        job_name = scrape_config["job_name"]
        if job_name == 'node':
            scrape_config["static_configs"][0]["targets"] = [os.getenv("NODE_EXPORTER_ENDPOINT") + ':' + os.getenv("NODE_EXPORTER_PORT")]
        elif job_name == 'blockchain':
            scrape_config["static_configs"][0]["targets"] = [os.getenv("BLOCKCHAIN_EXPORTER_ENDPOINT") + ':' + os.getenv("BLOCKCHAIN_EXPORTER_PORT")]
        elif job_name == 'cadvisor':
            scrape_config["static_configs"][0]["targets"] = [os.getenv("CADVISOR_EXPORTER_ENDPOINT") + ':' + os.getenv("CADVISOR_EXPORTER_PORT")]
        else:
            print(f'Unknown prometheus job name {job_name}')
        list_scrape_configs[idx] = scrape_config
    newdict["scrape_configs"] = list_scrape_configs
    with open(output_prometheus, "w") as f:
        yaml.dump(newdict, f)

if run_loki:
    with open(template_loki, "r") as f:
        newdict = yaml.safe_load(f)
    newdict["server"]["http_listen_port"] = os.getenv("LOKI_PORT")
    with open(output_loki, "w") as f:
        yaml.dump(newdict, f)

if run_provisoning_datasources:
    for source in ['loki', 'prometheus']:
        with open(f'{template_datasource}/{source}.yaml', "r") as f:
            newdict = yaml.safe_load(f)
        newdict["datasources"][0]["url"] = os.getenv(f'{source.upper()}_ENDPOINT') + ':' + os.getenv(f'{source.upper()}_PORT')
        with open(f'{output_datasource}/{source}.yaml', "w") as f:
            yaml.dump(newdict, f)

if run_contactpoint:
    with open(template_contactpoint, "r") as f:
        newdict = yaml.safe_load(f)
    newdict["contactPoints"][0]["receivers"][0]["settings"]["url"] = os.getenv("SLACK_WEBHOOK")
    with open(output_contactpoint, "w") as f:
        yaml.dump(newdict, f)

if run_client_promtail:
    with open(template_client_promtail, "r") as f:
        newdict = yaml.safe_load(f)
    newdict["clients"][0]["url"] = os.getenv('LOKI_ENDPOINT') + ':' + os.getenv('LOKI_PORT') + '/loki/api/v1/push'
    newdict["server"]["http_listen_port"] = os.getenv('PROMTAIL_PORT')
    with open(output_client_promtail, "w") as f:
        yaml.dump(newdict, f)

if run_client_bcexporter:
    with open(template_client_bcexporter, "r") as f:
        newdict = yaml.safe_load(f)
    newdict["exporter_port"] = os.getenv('BLOCKCHAIN_EXPORTER_PORT')
    with open(output_client_bcexporter, "w") as f:
        yaml.dump(newdict, f)

if run_docker_compose:
    with open(template_docker_compose, "r") as f:
        newdict = yaml.safe_load(f)
    list_services = newdict["services"]
    for (k, v) in list_services.items():
        if k not in ('loki', 'grafana', 'minio', 'prometheus', 'alertmanager', 'blockchain_exporter', 'promtail', 'node_exporter', 'cadvisor'):
            print(f'Unknown service {k} in docker-compose')
            continue
        list_services[f'{k}']['ports'] = [os.getenv(f'{k.upper()}_PORT') + ':' + os.getenv(f'{k.upper()}_PORT')]
    with open(output_docker_compose, "w") as f:
        yaml.dump(newdict, f)

