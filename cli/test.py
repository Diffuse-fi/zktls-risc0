import subprocess
import time
import sys
import socket

from utils.network import *
from deploy_feeder import deploy_data_feeder, request_storage_addresses
# from feed_feeder import prepare_json
from feed_feeder import feed_data
from feed_feeder import feed_data_legacy
from request_storage import do_request
from request_storage import method_enum
from parse_and_prove import prepare_json


def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=60):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False


anvil_testnet_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
os.environ["ETH_WALLET_PRIVATE_KEY"] = anvil_testnet_private_key

print("step 1: starting anvil...")
process = subprocess.Popen(["anvil"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if process.poll() is None:
    print("anvil started succesfully")
else:
    print("failed to start anvil")
    sys.exit(process.poll())


if is_port_open("localhost", 8545):
    print("Connection to localhost:8545 succeeded")
else:
    print("Connection to localhost:8545 failed")
    sys.exit(1)


print("step 2: deploying datafeed feeder...")
local_network = network_enum.LOCAL
deploy_data_feeder(local_network)

print("step 3: requesting storage addresses...")
for p in pair_name_enum:
    request_storage_addresses(local_network, p.value)

print("step 4: prepare data for feeder (test set 1)...")
prepare_json(False, True, False) # --binance, --test-data-1, --test-data-2

print("step 4: feed feeder...")
feed_data(local_network)

print("step 5: feed feeder legacy (neon compatible)...")
feed_data_legacy(local_network)

print("step 6: request storages...")
for p in pair_name_enum:
    for m in method_enum:
        do_request(p, local_network, m)

print("step 7: request and prove binance data...")
prepare_json(True, False, False) # --binance, --test-data-1, --test-data-2

print("step 8: feed feeder...")
feed_data(local_network)

print("step 9: feed feeder legacy (neon compatible)...")
feed_data_legacy(local_network)

print("step 10: request storages...")
for p in pair_name_enum:
    for m in method_enum:
        do_request(p, local_network, m)


print("step 11: terminate anvil")
process.terminate()