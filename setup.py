import argparse
import copy
import json
import os
import shutil
import stat
import sys
from pathlib import Path

import yaml


def load_yaml(yaml_path: str) -> dict:
    with open(Path(yaml_path), 'r') as f:
        template_dict = yaml.safe_load(f)
    return template_dict


def load_json(json_path: str) -> list:
    with open(Path(json_path), "r") as stream:
        return json.load(stream)


def generate_config(completed_template: dict, output_path: str):
    with open(Path(output_path), "w") as f:
        yaml.dump(completed_template, f)


def check_settings():
    def copy_settings():
        shutil.copy('templates/settings.yml', './settings.yml.new')
        sys.exit('Please update values in ./settings.yml.new and rename to ./settings.yml')

    if Path('./settings.yml').exists():
        current_version = load_yaml('./settings.yml')['version']
        template_version = load_yaml('templates/settings.yml')['version']
        if template_version > current_version:
            os.rename('./settings.yml', './settings.yml.old')
            copy_settings()
    else:
        copy_settings()


check_settings()
settings = load_yaml('settings.yml')


def update_prometheus_config():
    template_dict = load_yaml('templates/prometheus.yml')
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


def update_notification_policies():
    template_dict = load_yaml('templates/alerting/notificationpolicies.yaml')
    generate_config(template_dict, 'server/grafana_provisioning/alerting/notificationpolicies.yaml')


def convert_to_seconds(time_string: str) -> int:
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(time_string[:-1]) * seconds_per_unit[time_string[-1]]


def update_alerting():
    template_dict = load_yaml('templates/alerting/alerting.yaml')
    chains_list = load_json('clients/bcexporter/config/chains.json')
    default_range = settings["server"]["alerts"]["current_height"]["default_range"]
    overrides = settings["server"]["alerts"]["current_height"]["overrides"]
    overrides_list = []
    for chain in chains_list:
        curr_range = overrides.get(f'{chain["id"]}', default_range)
        temp_curr_height_alert_dict = copy.deepcopy(template_dict["groups"][0]["rules"][0])
        curr_range_in_secs = convert_to_seconds(curr_range)
        temp_curr_height_alert_dict["uid"] = f'{temp_curr_height_alert_dict["uid"]}_{chain["id"]}'
        temp_curr_height_alert_dict["title"] = f'{temp_curr_height_alert_dict["title"]}_{chain["id"]}'
        temp_curr_height_alert_dict["data"][0]["relativeTimeRange"]["from"] = curr_range_in_secs
        temp_curr_height_alert_dict["data"][0]["model"]["expr"] = temp_curr_height_alert_dict["data"][0]["model"]["expr"].replace('XXXX', f'{chain["id"]}')
        temp_curr_height_alert_dict["data"][2]["relativeTimeRange"]["from"] = curr_range_in_secs
        temp_curr_height_alert_dict["data"][2]["model"]["expr"] = temp_curr_height_alert_dict["data"][2]["model"]["expr"].replace('XXXX', f'{chain["id"]}')
        temp_curr_height_alert_dict["annotations"]["description"] = temp_curr_height_alert_dict["annotations"]["description"].replace('x time', curr_range)
        overrides_list.append(temp_curr_height_alert_dict)
    template_dict["groups"][0]["rules"] = overrides_list
    generate_config(template_dict, 'server/grafana_provisioning/alerting/alerting.yaml')


def map_contactpoint_parameter(receiver_idx: int, alert_name: str, alert_dict: dict, template_dict: dict):
    for parameter in alert_dict:
        if parameter == "addresses" and alert_name == "email":
            template_dict["contactPoints"][0]["receivers"][receiver_idx]["settings"]["addresses"] = ';'.join(alert_dict["addresses"])
        else:
            template_dict["contactPoints"][0]["receivers"][receiver_idx]["settings"][parameter] = alert_dict[parameter]


def update_alerting_contactpoint():
    template_dict = load_yaml('templates/alerting/contactpoint.yaml')
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


def update_docker_service_network_ports(stack: str, service_name: str, template_dict: dict):
    try:
        if settings[stack][service_name]["host_networking_enabled"]:
            template_dict["services"][service_name]["network_mode"] = "host"
            del template_dict["services"][service_name]['networks']
            del template_dict["services"][service_name]['ports']
    except KeyError:
        port_str = settings[stack][service_name]["port"]
        default_port_str = (template_dict["services"][service_name]['ports'][0]).split(':')[0]
        template_dict["services"][service_name]["ports"] = [f"{port_str}:{default_port_str}"]


def update_server_docker_compose():
    template_dict = load_yaml('templates/docker-compose.yml')
    for service_name in template_dict["services"].copy().keys():
        update_docker_service_network_ports('server', service_name, template_dict)
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
    template_dict = load_yaml("templates/clients/promtail-config.yml")
    domain = f"http://{settings['clients']['promtail']['loki_endpoint']}"
    loki_port = settings['clients']['promtail']['loki_port']
    full_url = f"{domain}:{loki_port}/loki/api/v1/push"
    template_dict["clients"][0]["url"] = full_url
    generate_config(template_dict, 'clients/promtail/promtail-config.yml')


def update_bcexporter():
    template_dict = load_yaml('templates/clients/config.yml')
    if settings["clients"]["blockchain_exporter"]["alias_enabled"]:
        template_dict["alias"] = settings["clients"]["blockchain_exporter"]["alias_name"]
    else:
        template_dict["alias"] = ""
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
    template_dict = load_yaml('templates/clients/docker-compose.yml')
    arg_clients = get_args().clients
    for service_name in template_dict["services"].copy().keys():
        if service_name in arg_clients:
            update_docker_service_network_ports('clients', service_name, template_dict)
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
    update_alerting()
    update_alerting_contactpoint()
    update_server_docker_compose()
    update_permissions_recursively('server/grafana/', 472, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)


if __name__ == "__main__":
    main()
