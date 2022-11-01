import os
import argparse
from pathlib import Path
import shutil
import yaml
from dotenv import load_dotenv

'''
This method parses several environment variables and returns the values in a dictionary.
'''


def _get_env_vars():
    env_vars = [
        "CLIENT_ENDPOINT", "SERVER_ENDPOINT"
        , "BLOCKCHAIN_EXPORTER_PORT", "PROMTAIL_PORT", "LOKI_PORT"
    ]
    env_var_dict = {}
    for env_var in env_vars:
        env_var_dict[env_var] = os.getenv(env_var)
    return env_var_dict


load_dotenv(dotenv_path=Path('../.env'))
env_vars = _get_env_vars()


def get_template(template_path):
    with open(template_path, 'r') as f:
        template_dict = yaml.safe_load(f)
    return template_dict


def generate_config(completed_template, output_path):
    with open(output_path, "w") as f:
        yaml.dump(completed_template, f)


def update_promtail():
    template_dict = get_template(
        Path("../templates/clients/promtail-config.yml"))
    template_dict["clients"][0]["url"] = f"http://{env_vars['SERVER_ENDPOINT']}:{env_vars['LOKI_PORT']}/loki/api/v1/push"
    template_dict["server"]["http_listen_port"] = int(env_vars["PROMTAIL_PORT"])
    generate_config(template_dict, Path('./promtail/promtail-config.yml'))


def update_bcexporter():
    template_dict = get_template(Path('../templates/clients/config.yml'))
    template_dict["exporter_port"] = int(env_vars['BLOCKCHAIN_EXPORTER_PORT'])
    generate_config(template_dict, Path('./bcexporter/config/config.yml'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clients', nargs='+', default=['blockchain_exporter', 'promtail', 'cadvisor', 'node_exporter']
                        , help='possible clients to run are blockchain_exporter, promtail, cadvisor, and node_exporter')

    args = parser.parse_args()
    clients = args.clients
    valid_args = ["blockchain_exporter",
                  "promtail", "cadvisor", "node_exporter"]

    update_bcexporter()
    update_promtail()

    for client in clients:
        if client not in valid_args:
            print(f"not a valid arg {client}")
        else:
            if client in valid_args:
                valid_args.remove(client)
            template_dict = get_template(
                Path('../templates/clients/docker-compose.yml'))
            for service in valid_args:
                del template_dict["services"][service]
            generate_config(template_dict, Path('./docker-compose.yml'))


if __name__ == "__main__":
    main()
