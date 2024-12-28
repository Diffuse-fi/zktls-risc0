# RISC Zero Ethereum Deployment Guide

Welcome to the [RISC Zero] Ethereum Deployment guide!

Once you've written your [contracts] and your [methods], and [tested] your program, you're ready to deploy your contract.

You can either:

- [Deploy your project to a local network][section-local]
- [Deploy to a testnet][section-testnet]
- [Deploy to Ethereum Mainnet][section-mainnet]

## Deploy your project on a local network using our CLI

You can deploy your contracts and run an end-to-end test or demo as follows:

1. Start a local testnet with `anvil` by running:

    ```bash
    anvil
    ```

    Once anvil is started, keep it running in the terminal, and switch to a new terminal.

2. Set your environment variables (remember, you need other key for testnet):
    ```bash
    # Anvil sets up a number of default wallets, and this private key is one of them.
    export ETH_WALLET_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
    ```

3. Build your project:

    ```bash
    cargo build
    ```
    run tests:

    ```bash
    cargo test
    forge test
    python3 cli/test.ry
    ```

4. Deploy data feeder contract by running:

    ```bash
    python3 cli/deploy_feeder.py -n local
    ```
    this contract creates storage contracts on deployment and writes proven data into them

5. Parse data from binance and create proof:

    ```bash
    python3 cli/parse_and_prove.py --binance
    ```
    also you can use already proven test data, it will work faster
    ```bash
    python3 cli/parse_and_prove.py --test-data-1
    ```

5. Deploy data to chain:

    ```bash
    python3 cli/feed_feeder.py -n local
    ```

6. Now You can request data from data feed storage:

    ```bash
    python3 cli/request_storage.py --network local --pair ETHBTC --method latestRoundData
    ```
    or

    ```bash
    python3 cli/request_storage.py --network local --pair BTCUSDT --method latestRoundData
    ```

7. Repeat parsing and proving

    ```bash
    python3 cli/feed_feeder.py --binance
    ```

8. Price onchain has changed:

    ```bash
    python3 cli/request_storage.py -n local -p BTCUSDT --m latestRoundData
    ```

## Interact with sepolia contract using our CLI

1. Set your environment variables (NOT the one from anvil! You need to change this viriable if you worked locally!):
    ```bash
    export ALCHEMY_API_KEY="YOUR_ALCHEMY_API_KEY" # the API_KEY provided with an alchemy account
    export ETH_WALLET_PRIVATE_KEY="YOUR_WALLET_PRIVATE_KEY" # the private hex-encoded key of your Sepolia testnet wallet
    ```

2. Build your project:

    ```bash
    cargo build
    ```
3. No instruction for deployment because contracts are already deployed

5. Parse data from binance and prove it:

    ```bash
    python3 cli/parse_and_prove.py --binance
    ```

5. publish it to sepolia:

    ```bash
    python3 cli/feed_feeder.py -n sepolia
    ```
    once proven, data can be reused, you can publish the same data on neon
    ```bash
    python3 cli/feed_feeder.py -n neon_devnet
    ```

6. Now You can request data from data feed storage:

    ```bash
    python3 cli/request_storage.py --network sepolia --pair BTCUSDT --method latestRoundData
    ```
    list of avaliable pairs is stored in cli/addresses/sepolia


## Deploy your project on a local network manually (I don't want to update these docs)

You can deploy your contracts and run an end-to-end test or demo as follows:

1. Start a local testnet with `anvil` by running:

    ```bash
    anvil
    ```

    Once anvil is started, keep it running in the terminal, and switch to a new terminal.

2. Set your environment variables:
    > ***Note:*** *This requires having access to a Bonsai API Key. To request an API key [complete the form here](https://bonsai.xyz/apply).*
    > Alternatively you can generate your proofs locally, assuming you have a machine with an x86 architecture and [Docker] installed. In this case do not export Bonsai related env variables.

    ```bash
    # Anvil sets up a number of default wallets, and this private key is one of them.
    export ETH_WALLET_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
    export BONSAI_API_KEY="YOUR_API_KEY" # see form linked in the previous section
    export BONSAI_API_URL="BONSAI_API_URL" # provided with your api key
    ```

3. Build your project:

    ```bash
    cargo build
    ```

4. Deploy your contract by running:

    ```bash
    forge script --rpc-url http://localhost:8545 --broadcast script/Deploy.s.sol
    ```

    This command should output something similar to:

    ```bash
    ...
    == Logs ==
    You are deploying on ChainID 31337
    Deployed RiscZeroGroth16Verifier to 0x5FbDB2315678afecb367f032d93F642f64180aa3
    Deployed DataFeedFeeder to 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
    ...
    ```

    Save the `DataFeedFeeder` contract address to an env variable:

    ```bash
    export DATA_FEEDER_ADDRESS=#COPY DATA FEEDER ADDRESS FROM DEPLOY LOGS
    ```

    > You can also use the following command to set the contract address if you have [`jq`][jq] installed:
    >
    > ```bash
    > export DATA_FEEDER_ADDRESS=$(jq -re '.transactions[] | select(.contractName == "DataFeedFeeder") | .contractAddress' ./broadcast/Deploy.s.sol/31337/run-latest.json)
    > ```

### Interact with your local deployment

1. Query the dataFeedStorage address of the ETHBTC pair

    ```bash
    cast call --rpc-url http://localhost:8545 ${DATA_FEEDER_ADDRESS:?} 'getPairStorageAddress(string)(address)' 'ETHBTC'
    ```
    Save the ETHBTC dataFeedStorage address to an env variable
    ```bash
    export ETHBTC_FEED_STORAGE_ADDRESS=#COPY ADDRESS FROM QUERY RESPONSE
    ```

2. Publish price data

    ```bash
    cargo run --bin publisher -- \
        --chain-id=31337 \
        --rpc-url= \
        --contract=${DATA_FEEDER_ADDRESS:?} \
        --json-path="test_inputs/01.json"
    ```

3. Query the state:

    ```bash
    cast call --rpc-url http://localhost:8545 ${ETHBTC_FEED_STORAGE_ADDRESS:?} 'latestRoundData()(uint80, uint256, uint256, uint256, uint80)'
    ```
    You will receive 5 numbers: last round Id, answer (price), startedAt(timestamp), updatedAt(same timestamp), answeredInRound (current round Id)

4. Publish next round of price data

    ```bash
    cargo run --bin publisher -- \
        --chain-id=31337 \
        --rpc-url=http://localhost:8545 \
        --contract=${DATA_FEEDER_ADDRESS:?} \
        --json-path="test_inputs/02.json"
    ```
5. Query the state:

    ```bash
    cast call --rpc-url http://localhost:8545 ${ETHBTC_FEED_STORAGE_ADDRESS:?} 'latestRoundData()(uint80, uint256, uint256, uint256, uint80)'
    ```
    Now the numbers will be changed to those specified in test_inputs/02.json


## Deploy your project on Sepolia testnet

You can deploy your contracts on the `Sepolia` testnet and run an end-to-end test or demo as follows:

1. Get access to Bonsai and an Ethereum node running on Sepolia testnet (in this example, we will be using [Alchemy](https://www.alchemy.com/) as our Ethereum node provider) and export the following environment variables:
    > ***Note:*** *This requires having access to a Bonsai API Key. To request an API key [complete the form here](https://bonsai.xyz/apply).*
    > Alternatively you can generate your proofs locally, assuming you have a machine with an x86 architecture and [Docker] installed. In this case do not export Bonsai related env variables.

    ```bash
    export BONSAI_API_KEY="YOUR_API_KEY" # see form linked in the previous section
    export BONSAI_API_URL="BONSAI_API_URL" # provided with your api key
    export ALCHEMY_API_KEY="YOUR_ALCHEMY_API_KEY" # the API_KEY provided with an alchemy account
    export ETH_WALLET_PRIVATE_KEY="YOUR_WALLET_PRIVATE_KEY" # the private hex-encoded key of your Sepolia testnet wallet
    ```

2. Build your project:

    ```bash
    cargo build
    ```

3. Deploy your contract by running:

    ```bash
    forge script script/Deploy.s.sol --rpc-url https://eth-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} --broadcast
    ```

    This command uses the `sepolia` profile defined in the [config][config] file, and should output something similar to:

    ```bash
    ...
    == Logs ==
    You are deploying on ChainID 11155111
    Deploying using config profile: sepolia
    Using IRiscZeroVerifier contract deployed at 0x925d8331ddc0a1F0d96E68CF073DFE1d92b69187
    Deployed DataFeedFeeder to 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
    ...
    ```

    Save the `DataFeedFeeder` contract address to an env variable:

    ```bash
    export DATA_FEEDER_ADDRESS=#COPY DATA FEEDER ADDRESS FROM DEPLOY LOGS
    ```

    > You can also use the following command to set the contract address if you have [`jq`][jq] installed:
    >
    > ```bash
    > export DATA_FEEDER_ADDRESS=$(jq -re '.transactions[] | select(.contractName == "DataFeedFeeder") | .contractAddress' ./broadcast/Deploy.s.sol/11155111/run-latest.json)
    > ```

### Interact with your Sepolia testnet deployment

1. Query the state:

    ```bash
    cast call --rpc-url https://eth-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} ${DATA_FEEDER_ADDRESS:?} 'get()(uint256, uint256)'
    ```

2. Publish a new state

    ```bash
    cargo run --bin publisher -- \
        --chain-id=11155111 \
        --rpc-url=https://eth-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} \
        --contract=${DATA_FEEDER_ADDRESS:?} \
        --input=1234 \
        --input=2=5678
    ```

3. Query the state again to see the change:

    ```bash
    cast call --rpc-url https://eth-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} ${DATA_FEEDER_ADDRESS:?} 'get()(uint256, uint256)'
    ```

## Deploy your project on Ethereum mainnet

You can deploy your contract on Ethereum Mainnet as follows:

1. Get access to Bonsai and an Ethereum node running on Mainnet (in this example, we will be using [Alchemy](https://www.alchemy.com/) as our Ethereum node provider) and export the following environment variables:
    > ***Note:*** *This requires having access to a Bonsai API Key. To request an API key [complete the form here](https://bonsai.xyz/apply).*
    > Alternatively you can generate your proofs locally, assuming you have a machine with an x86 architecture and [Docker] installed. In this case do not export Bonsai related env variables.

    ```bash
    export BONSAI_API_KEY="YOUR_API_KEY" # see form linked in the previous section
    export BONSAI_API_URL="BONSAI_API_URL" # provided with your api key
    export ALCHEMY_API_KEY="YOUR_ALCHEMY_API_KEY" # the API_KEY provided with an alchemy account
    export ETH_WALLET_ADDRESS="YOUR_WALLET_ADDRESS" # the account address you want to use for deployment
    ```

2. Build your project:

    ```bash
    cargo build
    ```

3. Deploy your contract by running:

    You'll need to pass options to forge script to connect to your deployer wallet. See the [Foundry documentation][forge-script-wallet-docs].
    The example command below configures Forge to use a Ledger hardware wallet.

    ```bash
    forge script script/Deploy.s.sol --rpc-url https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} --broadcast --ledger
    ```

    This command uses the `mainnet` profile defined in the [config][config] file, and should output something similar to:

    ```bash
    ...
    == Logs ==
    You are deploying on ChainID 1
    Deploying using config profile: mainnet
    Using IRiscZeroVerifier contract deployed at 0x8EaB2D97Dfce405A1692a21b3ff3A172d593D319
    Deployed DataFeedFeeder to 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
    ...
    ```

    Save the `DataFeedFeeder` contract address to an env variable:

    ```bash
    export DATA_FEEDER_ADDRESS=#COPY DATA FEEDER ADDRESS FROM DEPLOY LOGS
    ```

    > You can also use the following command to set the contract address if you have [`jq`][jq] installed:
    >
    > ```bash
    > export DATA_FEEDER_ADDRESS=$(jq -re '.transactions[] | select(.contractName == "DataFeedFeeder") | .contractAddress' ./broadcast/Deploy.s.sol/1/run-latest.json)
    > ```

### Interact with your Ethereum Mainnet deployment

1. Query the state:

    ```bash
    cast call --rpc-url https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} ${DATA_FEEDER_ADDRESS:?} 'get()(uint256, uint256)'
    ```

2. Publish a new state

    > NOTE: Currently only a local wallet, provided by the `ETH_WALLET_PRIVATE_KEY` env var is implemented in the example publisher app.
    > Please see https://github.com/risc0/risc0-foundry-template/issues/121 for more details.

    ```bash
    cargo run --bin publisher -- \
        --chain-id=1 \
        --rpc-url=https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} \
        --contract=${DATA_FEEDER_ADDRESS:?} \
        --input=1234 \
        --input=2=5678
    ```

3. Query the state again to see the change:

    ```bash
    cast call --rpc-url https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY:?} ${DATA_FEEDER_ADDRESS:?} 'get()(uint256, uint256)'
    ```

[section-mainnet]: #deploy-your-project-on-ethereum-mainnet
[section-local]: #deploy-your-project-on-a-local-network
[section-testnet]: #deploy-your-project-on-sepolia-testnet
[RISC Zero]: https://www.risczero.com/
[Docker]: https://docs.docker.com/engine/install/
[contracts]: ./contracts/
[jq]: https://jqlang.github.io/jq/
[methods]: ./methods/
[tested]: ./README.md#run-the-tests
[config]: ./script/config.toml
[forge-script-wallet-docs]: https://book.getfoundry.sh/reference/forge/forge-script#wallet-options---raw
