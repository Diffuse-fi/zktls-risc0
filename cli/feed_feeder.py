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


def feed_data(net, trace):
    if trace == True:
        feed_data_legacy(net, True)
    if net == network_enum.NEON_DEVNET:
        feed_data_legacy(net, False)
    else:
        feed_data_publisher(net)

def feed_data_publisher(net):
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


def feed_data_legacy(net, trace):
    latest_data_dir = "data/" + str(find_latest_data()) + "/"

    with open(latest_data_dir + "prices.txt") as prices_file:
        prices = prices_file.read()

    with open(latest_data_dir + "timestamps.txt") as timestamps_file:
        timestamps = timestamps_file.read()

    with open(latest_data_dir + "seal.bin", "rb") as file:
        bin_seal = file.read()
        hex_seal = '0x' + bin_seal.hex()

    with open(latest_data_dir + "hashed_json.bin", "rb") as file:
        bin_hashed_json = file.read()
        if bin_hashed_json:
            hex_hashed_json = '0x' + bin_hashed_json.hex()

    pairs = """["ETHBTC", "BTCUSDT", "ETHUSDT", "ETHUSDC"]"""

    method_signature = "set(string[4] memory pair_names,uint64[4] memory prices,uint64[4] memory timestamps,bytes calldata hashed_json,bytes calldata seal)"

    command = [
        "cast",
        "send",
        "--private-key=" + os.getenv("ETH_WALLET_PRIVATE_KEY"),
        "--legacy",
        rpc_url(net),
        get_feeder_address(net.value),
        method_signature,
        pairs,
        prices,
        timestamps,
        hex_hashed_json,
        hex_seal
    ]

    contract_bytecode_command = [
        "cast",
        "rpc",
        "eth_getCode",
        get_feeder_address(net.value),
        "latest",
        rpc_url(net)
    ]
    contract_bytecode = run_subprocess(contract_bytecode_command, "request contract bytecode")
    print("feeder contract bytecode:", contract_bytecode)

    if trace == True:
        command[1] = "call"
        command.append("--trace")
        remove_secrets_and_print(command)
        result = subprocess.run(command)
        print(result.stdout)
    else:
        remove_secrets_and_print(command)
        run_subprocess(command, "DataFeeder feeding")

def main():
    parser = argparse.ArgumentParser(description="Data feeder parameters")
    parser.add_argument('-n', '--network', type=parse_network, required=True, help="Choose network (local, sepolia, eth_mainnet, neon_devnet)")
    parser.add_argument('--trace', action='store_true', default=False, help="Print trace level logs using 'cast call --trace'")
    args = parser.parse_args()

    feed_data(args.network, args.trace)

if __name__ == "__main__":
    main()
