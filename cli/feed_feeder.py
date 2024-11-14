import sys
import argparse
from utils.network import *


def prepare_json (_binance_flag, test_data_1, test_data_2):

    latest_data = -1

    os.makedirs("data/", exist_ok=True)

    existing_data = os.listdir("data/")
    for d in existing_data:
        if (d.isdigit() == True):
            latest_data = max(latest_data, int(d))

    new_data_dir = "data/" + str(latest_data + 1) + "/"
    os.makedirs(new_data_dir)

    files = ["prover_input.json", "seal.bin", "journal.bin"]

    if test_data_1 == True:
        for f in files:
            run_subprocess(["cp", "test_data_1/0/" + f, new_data_dir + f], "copy" + " test_data_1/0/" + f + " to" + new_data_dir + f)

    elif test_data_2 == True:
        for f in files:
            run_subprocess(["cp", "test_data_2/0/" + f, new_data_dir + f], "copy" + " test_data_2/0/" + f + " to " + new_data_dir + f)

    elif _binance_flag == True:
        run_subprocess(["python3", "data-provider/script.py"], "request from binance")
        run_subprocess(["cp", "stripped_prices.json", new_data_dir + "prover_input.json"], "copy binance data to " + new_data_dir)

    else:
        print("expected either --test-data-1 or --test-data-2 or --binance flag")
        sys.exit(1)


def feed_data(net):
    command = [
        "cargo",
        "run",
        "--bin",
        "publisher",
        "--",
        chain_id(net),
        rpc_url(net),
        "--contract=" + get_feeder_address(net.value)
    ]

    run_subprocess(command, "DataFeeder feeding")


parser = argparse.ArgumentParser(description="Data feeder parameters")
parser.add_argument('-n', '--network', type=parse_network, required=True, help="Choose network (local, sepolia, eth_mainnet)")

data_source_group = parser.add_mutually_exclusive_group()
data_source_group.add_argument('--binance', action='store_true', help='Request data from binance and feed')
data_source_group.add_argument('--test-data-1', action='store_true', help='Take dataset from test_data_1/')
data_source_group.add_argument('--test-data-2', action='store_true', help='Take dataset from test_data_2')

args = parser.parse_args()


prepare_json(args.binance, args.test_data_1, args.test_data_2)
feed_data(args.network)

