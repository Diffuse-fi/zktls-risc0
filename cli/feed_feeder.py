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
        feed_data_legacy(net, False)
        # feed_data_publisher(net) // is deprecated, not needed anymore, will be just legacy feeder for now
        # should move to python web3 package I think

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

def text_array_from_binary_file(filename, isdigit):
    with open(filename, "rb") as f:
        data = f.read()
    text = data.decode("utf-8")
    text = text.rstrip('\x00')
    text = text.split('\n')

    if isdigit == True:
        quotation = ''
    else:
        quotation = '"'

    array = "["
    for line in text:
        if line != '\n':
            line = line.strip()
            line = quotation + line + quotation + ', '
            array += line
    array = array[:-2]
    array += "]"
    return array


def feed_data_legacy(net, trace):
    latest_data_dir = "data/" + str(find_latest_data()) + "/"

    pairs = text_array_from_binary_file(latest_data_dir + "pairs.bin", False)
    prices = text_array_from_binary_file(latest_data_dir + "prices.bin", True)
    timestamps = text_array_from_binary_file(latest_data_dir + "timestamps.bin", True)


    with open(latest_data_dir + "sgx_verification_seal.bin", "rb") as file:
        bin_sgx_verification_seal = file.read()
        hex_sgx_verification_seal = '0x' + bin_sgx_verification_seal.hex()

    with open(latest_data_dir + "sgx_verification_journal.bin", "rb") as file:
        bin_sgx_verification_journal = file.read()
        if bin_sgx_verification_journal:
            hex_sgx_verification_journal = '0x' + bin_sgx_verification_journal.hex()

    with open("pairs/amount.txt", "r") as file:
        pairs_amount = file.read().strip()

    method_signature = "set(string[" + pairs_amount + "] calldata pair_names,uint256[" + pairs_amount + "] calldata prices,uint256[" + pairs_amount + "] calldata timestamps,bytes calldata sgx_verification_journal,bytes calldata sgx_verification_seal)"

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
        hex_sgx_verification_journal,
        hex_sgx_verification_seal
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
