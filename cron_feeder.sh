#!/bin/bash

# add this script to cron:
# */10 * * * * /path_to_rep/zktls_risc0/runner.sh > /path_to_rep/zktls_risc0/cron_log.txt

export PATH="$HOME/.cargo/bin:$PATH"
export PATH="/$HOME/.foundry/bin:$PATH"

cd path_to_rep_from_home/zktls_risc0/

source .env

echo "start feeding: $(date)" >> feeding_log.txt
python3 cli/parse_and_prove.py --binance >> feeding_log.txt 2>&1
echo "binance data request and proving finished: $(date)" >> feeding_log.txt

python3 cli/feed_feeder.py --network=sepolia >> feeding_log.txt 2>&1
echo "sepolia feeding finished: $(date)" >> feeding_log.txt

python3 cli/feed_feeder.py --network=neon_devnet >> feeding_log.txt 2>&1
echo "neon_devnet feeding finished: $(date)" >> feeding_log.txt

echo "==========================================" >> feeding_log.txt
