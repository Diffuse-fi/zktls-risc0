key_file =  open('cli/anvil_private_key.txt', 'r')
private_key = key_file.readline().strip()
key_file.close()

import subprocess
import sys
import os

if not os.path.exists("cli/addresses/feeder"):
    os.makedirs("cli/addresses/feeder")

def deploy_data_feeder(what, command):
    print("===================================")
    result = subprocess.run(command, capture_output=True, text=True)
    exit_code = result.returncode
    print("stdout:")
    print(result.stdout)
    print("stderr:")
    print(result.stderr)
    if (exit_code == 0):
        print(what, "SUCCESSFUL!")
    else:
        print(what, "FAILED!")
        sys.exit(1)
    print("===================================")

    data_feeder_address = result.stdout.split("Deployed DataFeedFeeder to ")[1].split("\n")[0]
    file = open('cli/addresses/feeder/address.txt', 'w')
    file.write(data_feeder_address)
    file.close()


def request_storage_addresses(pair_name):
    file = open('cli/addresses/feeder/address.txt', 'r')
    data_feeder_address = file.readline().strip()
    file.close()

    command = [
        "cast",
        "call",
        "--rpc-url",
        "http://localhost:8545",
        data_feeder_address,
        "getPairStorageAddress(string)(address)",
        pair_name
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    exit_code = result.returncode

    if (exit_code == 0):
        print("Successfully requested DataFeedStorage address for", pair_name, ":", result.stdout)
        file = open('cli/addresses/' + pair_name + ".txt", 'w')
        file.write(result.stdout)
        file.close()
    else:
        print("DataFeedStorage address request for", pair_name, " has FAILED!")
        print(result.stderr)
        sys.exit(1)
    print("===================================")



deployment_command = [
    "forge",
    "script",
    "--rpc-url",
    "http://localhost:8545",
    "--broadcast",
    "script/Deploy.s.sol"
    ]

deploy_data_feeder("DataFeedFeeder deployment", deployment_command)

request_storage_addresses("ETHBTC")
request_storage_addresses("BTCUSDT")
request_storage_addresses("ETHUSDT")
request_storage_addresses("ETHUSDC")