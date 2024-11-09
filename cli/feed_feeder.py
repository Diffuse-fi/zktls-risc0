import subprocess
import sys

def feed_test_data(test_input_nr):
    file = open('cli/addresses/feeder/address.txt', 'r')
    data_feeder_address = file.readline().strip()
    file.close()

    command = [
        "cargo",
        "run",
        "--bin",
        "publisher",
        "--",
        "--chain-id=31337",
        "--rpc-url=http://localhost:8545",
        "--contract=" + data_feeder_address,
        "--json-path=test_inputs/0" + str(test_input_nr) + ".json"]

    result = subprocess.run(command, capture_output=True, text=True)

    exit_code = result.returncode

    if (exit_code == 0):
        print("Successfully feeded data_feeder")
        print(result.stdout)
    else:
        print("Data feeder feeding has FAILED!")
        print(result.stderr)
        sys.exit(1)
    print("===================================")

if len(sys.argv) > 1:
    number = int(sys.argv[1])
    feed_test_data(number)
else:
    print("Enter number of the test file you want to prove (1, 2)")

