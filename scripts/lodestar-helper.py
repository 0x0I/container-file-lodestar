#!/usr/bin/env python3

from datetime import datetime
import json
import os
import subprocess
import sys

import click
import requests
import urllib.request

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass

@cli.group()
def status():
    pass

###
# Commands for application configuration customization and inspection
###

DEFAULT_API_HOST_ADDR = 'http://localhost:5052'
DEFAULT_API_METHOD = 'GET'
DEFAULT_API_PATH = 'lighthouse/syncing'
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

@status.command()
@click.option('--host-addr',
              default=lambda: os.environ.get("API_HOST_ADDR", DEFAULT_API_HOST_ADDR),
              show_default=DEFAULT_API_HOST_ADDR,
              help='Lighthouse beacon or validator client Eth2 API host address in format <protocol(http/https)>://<IP>:<port>')
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
