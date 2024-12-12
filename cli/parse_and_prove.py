import sys
import argparse
from utils.network import *

def find_latest_data():
    latest_data = -1

    os.makedirs("data/", exist_ok=True)

    existing_data = os.listdir("data/")
    for d in existing_data:
        if (d.isdigit() == True):
            latest_data = max(latest_data, int(d))
    return latest_data


def prepare_json (_binance_flag, test_data_1, test_data_2):
    new_data_dir = "data/" + str(find_latest_data() + 1) + "/"
    os.makedirs(new_data_dir)

    files = ["prover_input.json", "seal.bin", "journal.bin", "prices.txt", "timestamps.txt"]

    if test_data_1 == True:
        for f in files:
            run_subprocess(["cp", "test_data_1/0/" + f, new_data_dir + f], "copy" + " test_data_1/0/" + f + " to" + new_data_dir + f)

    elif test_data_2 == True:
        f = "prover_input.json"
        run_subprocess(["cp", "test_data_2/0/" + f, new_data_dir + f], "copy" + " test_data_2/0/" + f + " to " + new_data_dir + f)

    elif _binance_flag == True:
        run_subprocess(["python3", "data-provider/script.py"], "request from binance")
        run_subprocess(["cp", "stripped_prices.json", new_data_dir + "prover_input.json"], "copy binance data to " + new_data_dir)
        prove_data()

    else:
        print("expected either --test-data-1 or --test-data-2 or --binance flag")
        sys.exit(1)


def prove_data():
    net = network_enum.SEPOLIA #placeholder, just need to create proof, any network will work
    command = [
        "cargo",
        "run",
        "--bin",
        "publisher",
        "--",
        chain_id(net),
        rpc_url(net),
        "--contract=" + get_feeder_address(net.value),
        "--do-not-publish"
    ]

    run_subprocess(command, "Proving")

def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")

    data_source_group = parser.add_mutually_exclusive_group()
    data_source_group.add_argument('--binance', action='store_true', help='Request data from binance and feed')
    data_source_group.add_argument('--test-data-1', action='store_true', help='Test set 1: input+proof (no proving needed)')
    data_source_group.add_argument('--test-data-2', action='store_true', help='Test set 2: input only (test proving)')

    args = parser.parse_args()

    prepare_json(args.binance, args.test_data_1, args.test_data_2)

if __name__ == "__main__":
    main()
