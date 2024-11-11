import subprocess
import sys
import os
from utils.network import *

def deploy_data_feeder(net):

    if net == network_enum.LOCAL:
        print("deploying DataFeedFeeder to", net.value)
    else:
        while(True):
            user_input = input("You are deploying DataFeeder to " + net.value + " network. Are you sure? [y/n]: ").lower()
            if user_input == 'y':
                break
            elif user_input == 'n':
                print("cancelled execution", file=sys.stderr)
                sys.exit(1)
            else:
                print("Please enter 'y' or 'n'.")
                continue


    deployment_command = ["forge", "script", rpc_url(net), chain_id(net), "--broadcast", "script/Deploy.s.sol"]
    result = run_subprocess(deployment_command, "DataFeedFeeder deployment")
    data_feeder_address = result.split("Deployed DataFeedFeeder to ")[1].split("\n")[0].strip()

    if (data_feeder_address.find('0x') != 0 or len(data_feeder_address) != 42):
        print("Deployment was successfull, but address parsing from server response FAILED", file=sys.stderr)
        print("expected address afrer \"Deployed DataFeedFeeder to\"\n", file=sys.stderr)
        print("response:", result, file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(os.path.dirname(address_path(net.value, "feeder"))):
        os.makedirs(os.path.dirname(address_path(net.value, "feeder")))

    file = open(address_path(net.value, "feeder"), 'w')
    file.write(data_feeder_address)
    print("wrote address to", address_path(net.value, "feeder"), "\n======================================")
    file.close()

    file.close()


def request_storage_addresses(net, pair_name):
    command = [ "cast", "call", rpc_url(net), get_feeder_address(net.value), "getPairStorageAddress(string)(address)", pair_name]
    result = run_subprocess(command, "request DataFeedStorage address for " + pair_name + " ")

    file = open(address_path(net.value, pair_name), 'w')
    print("wrote address to", address_path(net.value, pair_name), "\n======================================")
    file.write(result.strip())
    file.close()


parser = argparse.ArgumentParser(description="Data feeder parameters")
parser.add_argument('-n', '--network', type=parse_network, required=True, help="Choose network (local, sepolia, eth_mainnet)")

args = parser.parse_args()


deploy_data_feeder(args.network)

for p in pair_name_enum:
    request_storage_addresses(args.network, p.value)