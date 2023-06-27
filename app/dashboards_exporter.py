import os
import requests
import yaml

from logger import logger

GRAFANA_API_TOKEN_SOURCE = os.getenv('GRAFANA_API_TOKEN_SOURCE')
GRAFANA_API_TOKEN_DESTINATION = os.getenv('GRAFANA_API_TOKEN_DESTINATION')
GRAFANA_DOMAIN_SOURCE = os.getenv('GRAFANA_DOMAIN_SOURCE')
GRAFANA_DOMAIN_DESTINATION = os.getenv('GRAFANA_DOMAIN_DESTINATION')
CONFIG_FILE = os.getenv('CONFIG_PATH', 'config.yaml')

"""
Author: Luka Oberknezev
Initial commit: 23.6.2023.

When ran, this script will copy select folders and their dashboards from a source to a destination Grafana instance.
Make sure to specify the exact names of folders which are meant to be copied in config.yaml.
This script is meant to be run from job.sh bash script, and you need to define url and Grafana api keys for both source
and destination Grafana instances in here.

"""


def get_url(url, params=None):
    headers = {'accept-encoding': 'gzip',
               'Authorization': f'Bearer {GRAFANA_API_TOKEN_SOURCE}'}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except Exception as err:
        logger.critical(f"Failed getting URL: {err}")
        return False


def post_url(url, dashboard_definition):
    headers = {"Content-Type": 'application/json',
               'Authorization': f'Bearer {GRAFANA_API_TOKEN_DESTINATION}'}
    try:
        response = requests.post(url, json=dashboard_definition, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except Exception as err:
        logger.critical(f"Failed creating dashboard/folder: {err}")
        return False


def search_api():
    url = f"{GRAFANA_DOMAIN_SOURCE}/api/search"
    # Currently there is no pagination present and we are getting 5000 items in our response (both dashboards
    # and folders), which may possibly be improved upon.
    params = dict()
    params['limit'] = 5000
    url_response = get_url(url, params=params)
    if url_response:
        return url_response
    else:
        return list()


def get_folder_uid(folder_name, folders):

    for folder in folders:
        if folder['title'] == folder_name:
            return folder['uid']

    return None


def search_folders(query=''):
    url = f"{GRAFANA_DOMAIN_SOURCE}/api/folders"

    params = dict()
    params['limit'] = 5000
    params['query'] = query
    url_response = get_url(url, params=params)
    if url_response:
        return url_response
    else:
        return list()


def get_dashboard(uid):
    url = f"{GRAFANA_DOMAIN_SOURCE}/api/dashboards/uid/{uid}"
    url_response = get_url(url)
    if url_response:
        return url_response
    else:
        return {}


def create_folder(found_folders):
    url = f"{GRAFANA_DOMAIN_DESTINATION}/api/folders"
    url_response = post_url(url, found_folders)
    if url_response:
        return url_response
    else:
        return {}


def create_dashboard(dashboard_definition, folder_uid):
    url = f"{GRAFANA_DOMAIN_DESTINATION}/api/dashboards/db"
    del dashboard_definition['dashboard']['id']
    # Dashboard id needs to be deleted since every Grafana instance has its own id numbering order
    del dashboard_definition['meta']
    # Meta is deleted since when POST-ing the dashboard it will be ignored by the API
    dashboard_definition['folderUid'] = folder_uid
    # Folder uid needs to be set since by default a new random uid would be used
    dashboard_definition['overwrite'] = True
    url_response = post_url(url, dashboard_definition)
    if url_response:
        return url_response
    else:
        return {}


if __name__ == '__main__':
    with open(CONFIG_FILE, 'r') as file:
        folders = yaml.safe_load(file)['folders']
    found_all = search_api()
    for folder in folders:
        folder_uid = get_folder_uid(folder, found_all)
        folder_response = create_folder({'uid': folder_uid, 'title': folder})
        logger.info(f"This is created folder response for {folder}:\n {folder_response}")
        for dashboard in found_all:
            if dashboard['type'] == 'dash-db' and dashboard.get('folderUid', '') == folder_uid:
                # We set the default value of get folderUid to '' since the field doesn't exist if a dashboard is
                # placed in General folder and so the script will break if we don't specify this case.
                dashboard_definition = get_dashboard(dashboard['uid'])
                dashboard_response = create_dashboard(dashboard_definition, folder_uid)
                logger.info(f"This is created dashboard response for {dashboard['title']}:\n {dashboard_response}")
