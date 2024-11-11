import sys
import argparse
from utils.network import *


def prepare_json (_binance_flag, _test_set_nr, binance_json_file):
    if ((not _binance_flag) and (_test_set_nr is None)) == True:
        print("Use ether the --binance or --test-set-nr=1 or --test-set-nr=2 flag")
        sys.exit(1)

    test_input_file = "test_inputs/0" + str(_test_set_nr) + ".json"

    if _binance_flag:
        run_subprocess(["python3", "data-provider/script.py"], "request from binance")

    if _test_set_nr is not None:
        if not os.path.isfile(test_input_file):
            print(test_input_file, "file does not exist")
            sys.exit(1)
        run_subprocess(["cp", test_input_file, binance_json_file], "copy test input to prover input dir")


def feed_data(net, binance_json_file):
    command = [
        "cargo",
        "run",
        "--bin",
        "publisher",
        "--",
        chain_id(net),
        rpc_url(net),
        "--contract=" + get_feeder_address(net.value),
        "--json-path=" + binance_json_file
    ]

    run_subprocess(command, "DataFeeder feeding")


parser = argparse.ArgumentParser(description="Data feeder parameters")
parser.add_argument('-n', '--network', type=parse_network, required=True, help="Choose network (local, sepolia, eth_mainnet)")

data_source_group = parser.add_mutually_exclusive_group()
data_source_group.add_argument('--binance', action='store_true', help='Request data from binance and feed')
data_source_group.add_argument('-nr', '--test-set-nr', action='store', type=int, help='Take dataset from test_inputs/, possible values: 1,2')

args = parser.parse_args()


binance_json_file = "stripped_prices.json"
prepare_json(args.binance, args.test_set_nr, binance_json_file)
feed_data(args.network, binance_json_file)

