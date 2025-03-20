from solcx import compile_standard, install_solc
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_keyfile import extract_key_from_keyfile
import json, os, sys

def get_private_key(password,keystore_path):
    private_key = extract_key_from_keyfile(keystore_path, password.encode())

    print("Private Key:", private_key.hex())
    return private_key.hex()

def compile_smart_contract(filename):
    # Read the Solidity contract
    with open(filename, "r") as file:
        contract_content = file.read()

    # Compile the contract
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {filename: {"content": contract_content}},
            "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
        },
        solc_version="0.8.0",
    )

    # Save compiled output
    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    # Extract ABI & Bytecode
    abi = compiled_sol["contracts"]["hello_world.sol"]["HelloWorld"]["abi"]
    bytecode = compiled_sol["contracts"]["hello_world.sol"]["HelloWorld"]["evm"]["bytecode"]["object"]

    # Save ABI to a file
    with open("abi.json", "w") as file:
        json.dump(abi, file)

    print("Compilation successful! ABI and Bytecode saved.")

def deploy_contract(PRIVATE_KEY,ACCOUNT_ADDRESS,web3):

    assert web3.is_connected(), "Web3 is not connected!"

    # Load ABI & Bytecode
    with open("abi.json", "r") as file:
        abi = json.load(file)

    with open("compiled_code.json", "r") as file:
        compiled_sol = json.load(file)

    bytecode = compiled_sol["contracts"]["hello_world.sol"]["HelloWorld"]["evm"]["bytecode"]["object"]

    contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    # Create transaction
    tx = contract.constructor().build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gasPrice': "0x0",
    })

    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Deploying contract... Tx Hash: {tx_hash.hex()}")
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Contract deployed at: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

# Read the message
def get_message(contract):
    message = contract.functions.getMessage().call()
    print(f"Current Message: {message}")

# Update the message
def set_message(new_message,contract,PRIVATE_KEY,PUBLIC_KEY):
    tx = contract.functions.setMessage(new_message).build_transaction({
        'from': PUBLIC_KEY,
        'nonce': web3.eth.get_transaction_count(PUBLIC_KEY),
        'gasPrice': "0x0"
    })

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Updating message... Tx Hash: {tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)

if __name__ == "__main__":

    node_ip="localhost"
    node_port="8545"

    compile_smart_contract("hello_world.sol")

    # Connect to Ethereum network (local or testnet)
    HTTP_URL = f"http://{node_ip}:{node_port}"
    web3 = Web3(Web3.HTTPProvider(HTTP_URL))
    private_key = "8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
    public_key = Web3.to_checksum_address("fe3b557e8fb62b89f4916b721be55ceb828dbd73")
    #web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    # new_local_account = web3.eth.account.create()
    #
    # public_key = new_local_account.address
    # private_key = web3.to_hex(new_local_account.key)

    contract_address = deploy_contract(private_key,public_key,web3)
    """
    docker run -p 8545:8545 -p 8546:8546 -p 30303:30303 -v $PWD/ethash.json:/tmp/genesis.json --name besu_node hyperledger/besu:latest 
    --rpc-http-enabled --rpc-ws-enabled --miner-enabled --miner-coinbase fe3b557e8fb62b89f4916b721be55ceb828dbd73 --genesis-file=/tmp/genesis.json 
    --host-allowlist="*" --rpc-http-cors-origins="all" --profile=ENTERPRISE
    """

    # Load ABI
    with open("abi.json", "r") as file:
        abi = json.load(file)

    # Connect to contract
    contract = web3.eth.contract(address=contract_address, abi=abi)
    get_message(contract)

    set_message("Hello to you too!",contract,private_key,public_key)

    get_message(contract)
