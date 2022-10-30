from pathlib import Path
import yaml
import os
from dotenv import load_dotenv


'''
This method parses several environment variables and returns the values in a dictionary.
'''


def _get_env_vars():
    env_vars = [
        "NODE_EXPORTER_PORT", "BLOCKCHAIN_EXPORTER_PORT", "CADVISOR_EXPORTER_PORT"
        , "LOKI_PORT", "PROMETHEUS_PORT", "GRAFANA_PORT", "MINIO_PORT", "ALERTMANAGER_PORT"
        , "PROMTAIL_PORT", "SLACK_WEBHOOK", "MONITORING_ENDPOINT", "EXPORTER_ENDPOINT"
    ]
    env_var_dict = {}
    for env_var in env_vars:
        env_var_dict[env_var] = os.getenv(env_var)
    return env_var_dict


load_dotenv()
env_vars = _get_env_vars()


def get_template(template_path):
    with open(template_path, 'r') as f:
        template_dict = yaml.safe_load(f)
    return template_dict


def generate_config(completed_template, output_path):
    with open(output_path, "w") as f:
        yaml.dump(completed_template, f)


def update_prometheus_config():
    template_dict = get_template(Path('../templates/prometheus.yml'))
    for job_dict in template_dict["scrape_configs"]:
        if job_dict["job_name"] == "node":
            target = f"{env_vars['EXPORTER_ENDPOINT']}:{env_vars['NODE_EXPORTER_PORT']}"
            job_dict["static_configs"][0]["targets"] = [target]
        elif job_dict["job_name"] == "blockchain":
            target = f"{env_vars['EXPORTER_ENDPOINT']}:{env_vars['BLOCKCHAIN_EXPORTER_PORT']}"
            job_dict["static_configs"][0]["targets"] = [target]
        elif job_dict["job_name"] == "cadvisor":
            target = f"{env_vars['EXPORTER_ENDPOINT']}:{env_vars['CADVISOR_EXPORTER_PORT']}"
            job_dict["static_configs"][0]["targets"] = [target]
        else:
            print(f"Unexpected prometheus job found in config: {job_dict['job_name']}")
    generate_config(template_dict, Path('prometheus/prometheus.yml'))


def update_loki():
    template_dict = get_template(Path('../templates/loki-config.yml'))
    template_dict["server"]["http_listen_port"] = int(env_vars["LOKI_PORT"])
    generate_config(template_dict, Path('loki/loki-config.yml'))


def update_datasource(datasource):
    # if datasource.upper() != "LOKI" and datasource.upper() != "PROMETHEUS":
    if datasource.upper() not in ["LOKI", "PROMETHEUS", "ALERTMANAGER"]:
        print("invalid params passed for update_datasource")
    else:
        template_dict = get_template(
            Path(f'../templates/datasources/{datasource}.yaml'))
        endpoint = env_vars["MONITORING_ENDPOINT"]
        port = env_vars[f"{datasource.upper()}_PORT"]
        template_dict["datasources"][0]["url"] = f"http://{endpoint}:{port}"
        generate_config(template_dict, Path(
            f"grafana_provisioning/datasources/{datasource}.yaml"))


def update_alerting_contactpoint():
    template_dict = get_template(
        Path('../templates/alerting/contactpoint.yaml'))
    template_dict["contactPoints"][0]["receivers"][0]["settings"]["url"] = env_vars["SLACK_WEBHOOK"]
    generate_config(template_dict, Path(
        'grafana_provisioning/alerting/contactpoint.yaml'))


def update_root_docker_compose():
    template_dict = get_template(Path('../templates/docker-compose.yml'))
    services = ["loki", "minio", "grafana", "prometheus"]
    for service in services:
        port_str = env_vars[f"{service.upper()}_PORT"]
        template_dict["services"][service]['ports'] = [f"{port_str}:{port_str}"]
    generate_config(template_dict, Path("docker-compose.yml"))


def main():
    update_prometheus_config()
    update_loki()
    update_datasource("loki")
    update_datasource("prometheus")
    update_datasource("alertmanager")
    update_alerting_contactpoint()
    update_root_docker_compose()


if __name__ == "__main__":
    main()
