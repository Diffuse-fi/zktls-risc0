import os
import subprocess
import enum
import argparse
import sys

class pair_name_enum(enum.Enum):
    ETHBTC = "ETHBTC"
    BTCUSDT = "BTCUSDT"
    ETHUSDT = "ETHUSDT"
    ETHUSDC = "ETHUSDC"

def parse_pairname(value):
    try:
        return pair_name_enum(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid network: {value}. Possible valies: {[n.value for n in pair_name_enum]}")


class network_enum(enum.Enum):
    LOCAL = "local"
    SEPOLIA = "sepolia"
    NEON_DEVNET = "neon_devnet"
    ETH_MAINNET = "eth_mainnet"
    ASSET_TESTNET = "asset_testnet"

def parse_network(value):
    try:
        return network_enum(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid network: {value}. Possible valies: {[n.value for n in network_enum]}")


def address_path(net_val, contract):
    return 'cli/addresses/' + net_val + '/' + contract + '.txt'

def run_subprocess(_command, what):
    result = subprocess.run(_command, capture_output=True, text=True)

    exit_code = result.returncode

    if (exit_code == 0):
        print(what, "SUCCEEDED")
        return(result.stdout)
    else:
        print(what, "FAILED!")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)



def get_feeder_address(net_val):
    file = open(address_path(net_val, "feeder"), 'r')
    data_feeder_address = file.readline().strip()
    file.close()

    return data_feeder_address


def chain_id(net):
    match net:
        case network_enum.LOCAL:
            return "--chain-id=31337"
        case network_enum.SEPOLIA:
            return "--chain-id=11155111"
        case network_enum.NEON_DEVNET:
            return "--chain-id=245022926"
        case network_enum.ETH_MAINNET:
            return "--chain-id=1"
        case network_enum.ASSET_TESTNET:
            return "--chain-id=42421"

def rpc_url(net):
    alchemy_api_key = os.getenv('ALCHEMY_API_KEY')

    match net:
        case network_enum.LOCAL:
            return "--rpc-url=http://localhost:8545"
        case network_enum.SEPOLIA:
            return "--rpc-url=https://eth-sepolia.g.alchemy.com/v2/" + alchemy_api_key
        case network_enum.NEON_DEVNET:
            return "--rpc-url=https://devnet.neonevm.org"
        case network_enum.ETH_MAINNET:
            return "--rpc-url=https://eth-mainnet.g.alchemy.com/v2/" + alchemy_api_key
        case network_enum.ASSET_TESTNET:
            return "--rpc-url=https://enugu-rpc.assetchain.org/"