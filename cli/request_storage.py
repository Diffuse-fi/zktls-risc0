import subprocess
import sys
from datetime import datetime
from utils.network import *


class method_enum(enum.Enum):
    DECIMALS = "decimals"
    DESCRIPTION = "description"
    LATEST_ANSWER = "latestAnswer"
    LATEST_ROUND = "latestRound"
    LATEST_ROUND_DATA = "latestRoundData"

def parse_request(value):
    try:
        return method_enum(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid network: {value}. Possible valies: {[n.value for n in method_enum]}")

def get_request_signature(req):
    match req:
        case method_enum.DECIMALS:
            return "decimals()(uint8)"
        case method_enum.DESCRIPTION:
            return "description()(string)"
        case method_enum.LATEST_ANSWER:
            return "latestAnswer()(uint256)"
        case method_enum.LATEST_ROUND:
            return "latestRound()(uint256)"
        case method_enum.LATEST_ROUND_DATA:
            return "latestRoundData()(uint80, uint256, uint256, uint256, uint80)"

def do_request(pair, net, req):
    file = open('cli/addresses/' + net.value + '/' + pair.value + '.txt', 'r')
    storage_address = file.readline().strip()
    file.close()

    print("requesting method", req.value)

    command = [
        "cast",
        "call",
        rpc_url(net),
        storage_address,
        get_request_signature(req)
    ]

    result = run_subprocess(command, "request method '" + req.value + "' for " + pair.value)

    if req == method_enum.LATEST_ROUND_DATA:
        result = result.split("\n")
        print("round number:", result[0])
        print("answer:", result[1], "(price:", int(result[1].split(" [")[0]) / 100000, ")")

        timestamp = int(int(result[2].split(" [")[0]) / 1000)
        readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print("timestamp:", timestamp, "(human readable:)", readable_date)
    else:
        print("result:", result)
    print("===================================")


def main():
    parser = argparse.ArgumentParser(description="Storage request parameters")
    parser.add_argument('-n', '--network', type=parse_network, required=True, help="Choose network (local, sepolia, eth_mainnet)")
    parser.add_argument('-p', '--pair', type=parse_pairname, required=True, help="Choose pair (ETHBTC, BTCUSDT, ETHUSDT, ETHUSDC)")
    parser.add_argument('-m', '--method', type=parse_request, required=True,
        help="Choose request (decimals, description, latestAnswer, latestRound, latestRoundData)")

    args = parser.parse_args()

    do_request(args.pair, args.network, args.method)

if __name__ == "__main__":
    main()