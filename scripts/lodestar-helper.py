#!/usr/bin/env python3

from datetime import datetime
import json
import os
import subprocess
import sys

import click
import urllib.request
import yaml


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass

@cli.group()
def config():
    pass

@cli.group()
def status():
    pass

###
# Commands for application configuration customization and inspection
###

DEFAULT_LODESTAR_CONFIG_PATH = "{dir}/config.yml".format(dir=os.environ.get("CONF_DIR", "/etc/lodestar"))
DEFAULT_API_HOST_ADDR = 'http://localhost:9596'
DEFAULT_API_METHOD = 'GET'
DEFAULT_API_PATH = 'eth/v1/node/identity'
DEFAULT_API_DATA = '{}'


def print_json(json_blob):
    print(json.dumps(json_blob, indent=4, sort_keys=True))

def execute_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode > 0:
        print('Executing command \"%s\" returned a non-zero status code %d' % (command, process.returncode))
        sys.exit(process.returncode)

    if error:
        print(error.decode('utf-8'))

    return output.decode('utf-8')

@config.command()
@click.option('--config-path',
              default=lambda: os.environ.get("LODESTAR_CONFIG", DEFAULT_LODESTAR_CONFIG_PATH),
              show_default=DEFAULT_LODESTAR_CONFIG_PATH,
              help='path to lodestar configuration file to generate or customize from environment config settings')
def customize(config_path):
    config_dict = dict()
    if os.path.isfile(config_path):
        with open(config_path, "r") as stream:
            try:
                config_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    for var in os.environ.keys():
        var_split = var.split('_')
        if len(var_split) == 2 and var_split[0].lower() == "config":
            config_setting = var_split[1]
            value = os.environ[var]

            # ensure values are cast appropriately
            if value.isdigit():
                value = int(value)
            elif value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            config_dict[config_setting] = value

    with open(config_path, 'w+') as f:
        yaml.dump(config_dict, f)

    # remove surrounding quotes from ALL list setting values if necessary
    subprocess.call(['sed -i "s/\'\[/\[/g" {path}'.format(path=config_path)], shell=True)
    subprocess.call(['sed -i "s/\]\'/\]/g" {path}'.format(path=config_path)], shell=True)

@status.command()
@click.option('--host-addr',
              default=lambda: os.environ.get("API_HOST_ADDR", DEFAULT_API_HOST_ADDR),
              show_default=DEFAULT_API_HOST_ADDR,
              help='Lodestar beacon client Eth2 API host address in format <protocol(http/https)>://<IP>:<port>')
@click.option('--api-method',
              default=lambda: os.environ.get("API_METHOD", DEFAULT_API_METHOD),
              show_default=DEFAULT_API_METHOD,
              help='HTTP method to execute a part of request')
@click.option('--api-path',
              default=lambda: os.environ.get("API_PATH", DEFAULT_API_PATH),
              show_default=DEFAULT_API_PATH,
              help='Restful API path to target resource')
@click.option('--api-data',
              default=lambda: os.environ.get("API_DATA", DEFAULT_API_DATA),
              show_default=DEFAULT_API_DATA,
              help='Restful API request body data included within POST requests')
def api_request(host_addr, api_method, api_path, api_data):
    """
    Execute RESTful API HTTP request
    """

    try:
        if api_method.upper() == "POST":
            resp = requests.post(
                "{host}/{path}".format(host=host_addr, path=api_path),
                json=json.loads(api_data),
                headers={'Content-Type': 'application/json'})
        else:
            resp = requests.get("{host}/{path}".format(host=host_addr, path=api_path))

        # signal error if non-OK response status
        resp.raise_for_status()

        print_json(resp.json())
    except requests.exceptions.RequestException as err:
        sys.exit(print_json({
            "error": "API request to {host} failed with: {error}".format(
                host=host_addr,
                error=err
            )
        }))
    except json.decoder.JSONDecodeError:
        print(resp.text)


if __name__ == "__main__":
    cli()
