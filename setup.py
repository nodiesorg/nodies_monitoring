import argparse
import os
import stat
from pathlib import Path

import yaml


def get_template(template_path: str) -> dict:
    with open(Path(template_path), 'r') as f:
        template_dict = yaml.safe_load(f)
    return template_dict


def get_settings():
    return get_template("settings.yml")


def generate_config(completed_template: dict, output_path: str):
    with open(Path(output_path), "w") as f:
        yaml.dump(completed_template, f)


settings = get_settings()

def update_prometheus_config():
    template_dict = get_template('templates/prometheus.yml')
    for job_dict in template_dict["scrape_configs"]:
        if job_dict["job_name"] == "node":
            targets = settings["server"]["prometheus"]["exporter_endpoints"]["node"]
            job_dict["static_configs"][0]["targets"] = targets
        elif job_dict["job_name"] == "blockchain":
            targets = settings["server"]["prometheus"]["exporter_endpoints"]["blockchain"]
            job_dict["static_configs"][0]["targets"] = targets
        elif job_dict["job_name"] == "cadvisor":
            targets = settings["server"]["prometheus"]["exporter_endpoints"]["cadvisor"]
            job_dict["static_configs"][0]["targets"] = targets
        else:
            print(
                f"Unexpected prometheus job found in config: {job_dict['job_name']}")
    generate_config(template_dict, 'server/prometheus/prometheus.yml')


def update_loki():
    template_dict = get_template('templates/loki-config.yml')
    template_dict["server"]["http_listen_port"] = settings["server"]["loki"]["port"]
    generate_config(template_dict, 'server/loki/loki-config.yml')


def update_datasource(datasource: str):
    template_dict = get_template(f'templates/datasources/{datasource}.yaml')
    endpoint = settings["server"]["host_ip"]
    port = settings["server"][datasource]["port"]
    template_dict["datasources"][0]["url"] = f"http://{endpoint}:{port}"
    generate_config(template_dict, f"server/grafana_provisioning/datasources/{datasource}.yaml")


def update_notification_policies():
    template_dict = get_template('templates/alerting/notificationpolicies.yaml')
    generate_config(template_dict, 'server/grafana_provisioning/alerting/notificationpolicies.yaml')


def convert_to_seconds(time_string: str) -> int:
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(time_string[:-1]) * seconds_per_unit[time_string[-1]]


def update_alerting():
    template_dict = get_template('templates/alerting/alerting.yaml')
    stale_range = settings["server"]["alerts"]["stale_range"]
    template_dict["groups"][0]["rules"][0]["data"][0]["relativeTimeRange"]["from"] = convert_to_seconds(stale_range)
    template_dict["groups"][0]["rules"][0]["data"][2]["relativeTimeRange"]["from"] = convert_to_seconds(stale_range)
    template_dict["groups"][0]["rules"][0]["annotations"]["description"] = template_dict["groups"][0]["rules"][0]["annotations"]["description"].replace('x time', stale_range)
    generate_config(template_dict, 'server/grafana_provisioning/alerting/alerting.yaml')


def map_contactpoint_parameter(receiver_idx: int, alert_name: str, alert_dict: dict, template_dict: dict):
    for parameter in alert_dict:
        if parameter == "addresses" and alert_name == "email":
            template_dict["contactPoints"][0]["receivers"][receiver_idx]["settings"]["addresses"] = ';'.join(alert_dict["addresses"])
        else:
            template_dict["contactPoints"][0]["receivers"][receiver_idx]["settings"][parameter] = alert_dict[parameter]


def update_alerting_contactpoint():
    template_dict = get_template('templates/alerting/contactpoint.yaml')
    valid_args = ["slack", "discord", "teams", "email", "webhook"]
    for alert_name, alert_dict in settings["server"]["alerts"]["contactpoints"].items():
        if alert_name not in valid_args:
            print(f"not a supported contactpoint {alert_name}")
        else:
            for idx, receiver_dict in enumerate(template_dict["contactPoints"][0]["receivers"]):
                if receiver_dict["type"] == alert_name:
                    if alert_dict["enabled"]:
                        map_contactpoint_parameter(idx, alert_name, alert_dict, template_dict)
                        if not Path('server/grafana_provisioning/alerting/notificationpolicies.yaml').exists():
                            update_notification_policies()
                    else:
                        template_dict["contactPoints"][0]["receivers"].pop(idx)
    generate_config(template_dict, 'server/grafana_provisioning/alerting/contactpoint.yaml')


def update_server_docker_compose():
    template_dict = get_template('templates/docker-compose.yml')
    services = ["loki", "minio", "grafana", "prometheus"]
    for service in services:
        port_str = settings["server"][service]["port"]
        default_port_str = (template_dict["services"][service]['ports'][0]).split(':')[0]
        template_dict["services"][service]['ports'] = [f"{port_str}:{default_port_str}"]
    generate_config(template_dict, "server/docker-compose.yml")


def update_permissions_recursively(dir_path: str, user_id: int, perms: int):
    # update root directory
    dir_path = Path(dir_path)
    os.chown(dir_path, user_id, -1)
    os.chmod(dir_path, perms)
    for root, dirs, files in os.walk(dir_path):
        # update sub directories
        for dir in dirs:
            os.chown(os.path.join(root, dir), user_id, -1)
            os.chmod(os.path.join(root, dir), perms)
        # update sub files
        for file in files:
            os.chown(os.path.join(root, file), user_id, -1)
            os.chmod(os.path.join(root, file), perms)


# client update methods
def update_promtail():
    template_dict = get_template("templates/clients/promtail-config.yml")
    domain = f"http://{settings['clients']['promtail']['loki_endpoint']}"
    loki_port = settings['clients']['promtail']['loki_port']
    full_url = f"{domain}:{loki_port}/loki/api/v1/push"
    promtail_port = settings["clients"]["promtail"]["port"]

    template_dict["clients"][0]["url"] = full_url
    template_dict["server"]["http_listen_port"] = int(promtail_port)
    generate_config(template_dict, 'clients/promtail/promtail-config.yml')


def update_bcexporter():
    blockchain_exporter_port = settings["clients"]["blockchain_exporter"]["port"]
    template_dict = get_template('templates/clients/config.yml')
    template_dict["exporter_port"] = blockchain_exporter_port
    if settings["clients"]["blockchain_exporter"]["alias_enabled"]:
        template_dict["alias"] = settings["clients"]["blockchain_exporter"]["alias_name"]
    else:
        template_dict["alias"]=""
    generate_config(template_dict, 'clients/bcexporter/config/config.yml')


def get_args() -> argparse.Namespace:
    valid_args = ["blockchain_exporter", "promtail", "cadvisor", "node_exporter"]
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clients', nargs='+', default=['blockchain_exporter', 'promtail', 'cadvisor',
                                                               'node_exporter'],
                        help='possible clients to run are blockchain_exporter, promtail, cadvisor, and node_exporter')
    args = parser.parse_args()
    for client in args.clients.copy():
        if client not in valid_args:
            print(f"not a valid arg {client}")
            args.clients.remove(client)
    return args


def update_clients_docker_compose():
    template_dict = get_template('templates/clients/docker-compose.yml')
    arg_clients = get_args().clients
    for service_name, service_dict in template_dict["services"].copy().items():
        if service_name in arg_clients:
            port_str = settings["clients"][service_name]["port"]
            default_port_str = (template_dict["services"][service_name]['ports'][0]).split(':')[0]
            template_dict["services"][service_name]["ports"] = [f"{port_str}:{default_port_str}"]
            if service_name == 'promtail':
                promtail_log_root_path = settings["clients"]["promtail"]["log_root_path"]
                for idx, promtail_volume in enumerate(template_dict["services"][service_name]["volumes"]):
                    if promtail_volume.endswith('/var/log'):
                        template_dict["services"][service_name]["volumes"][idx] = f"{promtail_log_root_path}:/var/log"
        else:
            del template_dict["services"][service_name]
    generate_config(template_dict, 'clients/docker-compose.yml')


def main():
    # client
    update_clients_docker_compose()
    update_bcexporter()
    update_promtail()

    # server
    update_prometheus_config()
    update_loki()
    update_datasource("loki")
    update_datasource("prometheus")
    update_alerting()
    update_alerting_contactpoint()
    update_server_docker_compose()
    update_permissions_recursively('server/grafana/', 472, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)


if __name__ == "__main__":
    main()
