import subprocess
import sys

def get(pair_name, request_name):
    file = open('cli/addresses/' + pair_name + '.txt', 'r')
    storage_address = file.readline().strip()
    file.close()

    match request_name:
        case "decimals":
            request_prod = 'decimals()(uint8)'
        case "description":
            request_prod = 'description()(string)'
        case "latestAnswer":
            request_prod = 'latestAnswer()(uint256)'
        case "latestRound":
            request_prod = 'latestRound()(uint256)'
        case _:
            request_prod = 'latestRoundData()(uint80, uint256, uint256, uint256, uint80)'

    print("requesting method", request_prod)

    command = ["cast", "call", "--rpc-url", "http://localhost:8545", storage_address, request_prod]


    result = subprocess.run(command, capture_output=True, text=True)

    exit_code = result.returncode

    if (exit_code == 0):
        print("Successfully requested data from storage")
        if (request_prod != 'latestRoundData()(uint80, uint256, uint256, uint256, uint80)'):
            print(result.stdout)
        else:
            res = result.stdout
            res = res.split("\n")
            print("round number:", res[0])
            print("answer:", res[1], "(price:", int(res[1].split(" [")[0]) / 100000, ")")
            print("timestamp:", res[2])
    else:
        print("Storage request has failed")
        print(result.stderr)
        sys.exit(1)
    print("===================================")

if len(sys.argv) == 2:
    pair = sys.argv[1]
    get(pair, "")
elif len(sys.argv) > 2:
    pair = sys.argv[1]
    request = sys.argv[2]
    get(pair, request)
else:
    print("Enter pair name and request")



