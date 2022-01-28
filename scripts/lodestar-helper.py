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

###
# Commands for application configuration customization and inspection
###

DEFAULT_LODESTAR_CONFIG_PATH = "{dir}/config.yml".format(dir=os.environ.get("LODESTAR_CONFIG_DIR", "/etc/lodestar"))


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


if __name__ == "__main__":
    cli()
