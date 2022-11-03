import os
import stat
import argparse
from pathlib import Path
import yaml


def get_template(template_path):
    with open(template_path, 'r') as f:
        template_dict = yaml.safe_load(f)
    return template_dict


def get_settings():
    return get_template("settings.yml")


def generate_config(completed_template, output_path):
    with open(output_path, "w") as f:
        yaml.dump(completed_template, f)


settings = get_settings()

# server update methods


def update_prometheus_config():
    template_dict = get_template(Path('templates/prometheus.yml'))
    for job_dict in template_dict["scrape_configs"]:
        if job_dict["job_name"] == "node":
            targets = settings["server"]["exporter_endpoints"]["node"]
            job_dict["static_configs"][0]["targets"] = targets
        elif job_dict["job_name"] == "blockchain":
            targets = settings["server"]["exporter_endpoints"]["blockchain"]
            job_dict["static_configs"][0]["targets"] = targets
        elif job_dict["job_name"] == "cadvisor":
            targets = settings["server"]["exporter_endpoints"]["cadvisor"]
            job_dict["static_configs"][0]["targets"] = targets
        else:
            print(
                f"Unexpected prometheus job found in config: {job_dict['job_name']}")
    generate_config(template_dict, Path('server/prometheus/prometheus.yml'))


def update_loki():
    template_dict = get_template(Path('templates/loki-config.yml'))
    template_dict["server"]["http_listen_port"] = settings["server"]["ports"]["loki"]
    generate_config(template_dict, Path('server/loki/loki-config.yml'))


def update_datasource(datasource):
    template_dict = get_template(
        Path(f'templates/datasources/{datasource}.yaml'))
    endpoint = settings["server"]["endpoint"]
    port = settings["server"]["ports"][datasource]
    template_dict["datasources"][0]["url"] = f"http://{endpoint}:{port}"
    generate_config(template_dict, Path(
        f"server/grafana_provisioning/datasources/{datasource}.yaml"))


def update_alerting_contactpoint():
    template_dict = get_template(
        Path('templates/alerting/contactpoint.yaml'))
    template_dict["contactPoints"][0]["receivers"][0]["settings"]["url"] = settings["server"]["slack"]["webhook"]
    generate_config(template_dict, Path(
        'server/grafana_provisioning/alerting/contactpoint.yaml'))


def update_server_docker_compose():
    template_dict = get_template(Path('templates/docker-compose.yml'))
    services = ["loki", "minio", "grafana", "prometheus"]
    for service in services:
        port_str = settings["server"]["ports"][service]
        template_dict["services"][service]['ports'] = [
            f"{port_str}:{port_str}"]
    generate_config(template_dict, Path("server/docker-compose.yml"))


def update_grafana_folder_permissions():
    grafana_path = Path('server/grafana/')
    perms = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH

    def recursive_perms(path, permissions):
        # update root directory
        os.chown(path, 472, -1)
        os.chmod(path, permissions)
        for root, dirs, files in os.walk(path):
            # update sub directories
            for dir in dirs:
                os.chown(os.path.join(root, dir), 472, -1)
                os.chmod(os.path.join(root, dir), permissions)
            # update sub files
            for file in files:
                os.chown(os.path.join(root, file), 472, -1)
                os.chmod(os.path.join(root, file), permissions)

    recursive_perms(grafana_path, perms)

# client update methods
def update_promtail():
    template_dict = get_template(
        Path("templates/clients/promtail-config.yml"))
    domain = f"http://{settings['server']['endpoint']}"
    loki_port = settings['clients']['ports']['loki']
    full_url = f"{domain}:{loki_port}/loki/api/v1/push"
    promtail_port = settings["clients"]["ports"]["promtail"]

    template_dict["clients"][0]["url"] = full_url
    template_dict["server"]["http_listen_port"] = int(promtail_port)
    generate_config(template_dict, Path(
        'clients/promtail/promtail-config.yml'))


def update_bcexporter():
    blockchain_exporter_port = settings["clients"]["ports"]["blockchain_exporter"]
    template_dict = get_template(Path('templates/clients/config.yml'))
    template_dict["exporter_port"] = blockchain_exporter_port
    generate_config(template_dict, Path(
        'clients/bcexporter/config/config.yml'))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clients', nargs='+', default=['blockchain_exporter', 'promtail', 'cadvisor',
                        'node_exporter'], help='possible clients to run are blockchain_exporter, promtail, cadvisor, and node_exporter')

    args = parser.parse_args()
    return args


def update_clients_docker_compose():
    args = get_args()
    clients = args.clients
    valid_args = ["blockchain_exporter",
                  "promtail", "cadvisor", "node_exporter"]
    removed_list = valid_args
    # generate the client docker compose
    for client in clients:
        if client not in valid_args:
            print(f"not a valid arg {client}")
        else:
            template_dict = get_template(
                Path('templates/clients/docker-compose.yml'))
            for service in valid_args:
                port = settings["clients"]["ports"][service]
                template_dict["services"][service]["ports"] = [
                    f"{port}:{port}"]
            if client in valid_args:
                removed_list.remove(client)
            for service in removed_list:
                del template_dict["services"][service]
            generate_config(template_dict, Path(
                'clients/docker-compose.yml'))


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
    update_alerting_contactpoint()
    update_server_docker_compose()
    update_grafana_folder_permissions()


if __name__ == "__main__":
    main()
