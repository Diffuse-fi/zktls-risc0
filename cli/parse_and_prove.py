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


def prepare_json (_binance_flag, test_data_1):
    new_data_dir = "data/" + str(find_latest_data() + 1) + "/"
    os.makedirs(new_data_dir)

    files_1 = ["pairs.bin", "prices.bin", "timestamps.bin", "sgx_quote.bin"]
    files_2 = ["sgx_verification_journal.bin", "sgx_verification_seal.bin"]

    if test_data_1 == True:
        for f in files_1:
            run_subprocess(["cp", "test_data_1/0/" + f, new_data_dir + f], "copy" + " test_data_1/0/" + f + " to" + new_data_dir + f)

    elif _binance_flag == True:
        run_subprocess(["./lib/sgx-scaffold/target/debug/app-template"], "request from binance using sgx")
        for f in files_1:
            run_subprocess(["cp", f, new_data_dir + f], "copy requested " + f + " to " + new_data_dir)

        run_subprocess(["./lib/automata-dcap-zkvm-cli/target/release/dcap-bonsai-cli", "prove", "-p", new_data_dir + "sgx_quote.bin"], "prove sgx_quote verification")

        for f in files_2:
            run_subprocess(["cp", f, new_data_dir + f], "copy requested " + f + " to " + new_data_dir)

    else:
        print("expected either --test-data-1 or --test-data-2 or --binance flag")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")

    data_source_group = parser.add_mutually_exclusive_group()
    data_source_group.add_argument('--binance', action='store_true', help='Request data from binance and prove')
    data_source_group.add_argument('--test-data', action='store_true', help='Test set 1: prove existing data and sgx quote')

    args = parser.parse_args()

    prepare_json(args.binance, args.test_data)

if __name__ == "__main__":
    main()
