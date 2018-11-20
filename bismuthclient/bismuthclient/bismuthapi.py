"""
Wrapper around the official Bismuth API from api.bismuth.live

WIP
"""

import logging
import requests
import time

# Light wallet benchmark and helpers
from bismuthclient import lwbench

__version__ = '0.0.1'


def get_wallet_servers_legacy(light_ip_list='', app_log=None):
    """
    Use different methods to return the best possible list of wallet servers,
    sorted
    ip:port"""

    if not app_log:
        app_log = logging

    while True:
        # If we have 127.0.0.1 in the list, first try it
        if '127.0.0.1:5658' in light_ip_list or '127.0.0.1' in light_ip_list:
            if lwbench.connectible('127.0.0.1:5658'):
                # No need to go further.
                return ['127.0.0.1:5658']

        # Then try the new API
        wallets = []
        try:
            rep = requests.get("http://api.bismuth.live/servers/wallet/legacy.json")
            if rep.status_code == 200:
                wallets = rep.json()
        except Exception as e:
            app_log.warning("Error {} getting Server list from API, using lwbench instead".format(e))

        if not wallets:
            # no help from api, use previous benchmark
            ipport_list = lwbench.time_measure(light_ip_list, app_log)
            return ipport_list

        # We have a server list, order by load
        sorted_wallets = sorted([wallet for wallet in wallets if wallet['active']], key=lambda k: (k['clients']+1)/(k['total_slots']+2))

        if sorted_wallets:
            return ["{}:{}".format(wallet['ip'], wallet['port']) for wallet in sorted_wallets]

        # If we get here, all hope is lost!
        app_log.warning("No connectible server... let try again in a few sec")
        time.sleep(10)