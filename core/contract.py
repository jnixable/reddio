from core.config import REDDIO_CHAIN_ID, REDDIO_RPC_URL
from core.utils import generate_random_name, get_account, random_between
from web3 import Web3
from solcx import compile_source, install_solc, set_solc_version


def setup_solc():
    install_solc('0.8.0')
    set_solc_version('0.8.0')

func_name1 = generate_random_name(10)
func_name2 = generate_random_name(10)
CONTRACT_SOURCE = """pragma solidity ^0.8.0;contract TestContract {    uint256 private value;    constructor(uint256 initialValue) {        value = initialValue;    }    function """ + func_name1 + """(uint256 newValue) public {        value = newValue;    }    function """ + func_name2 + """() public view returns (uint256) {        return value;    }}"""

def deploy_contract(private_key):
  
    setup_solc()

    web3 = Web3(Web3.HTTPProvider(REDDIO_RPC_URL))

    compiled_sol = compile_source(CONTRACT_SOURCE)
    contract_interface = compiled_sol['<stdin>:TestContract']

    contract = web3.eth.contract(
        abi=contract_interface['abi'],        
        bytecode=contract_interface['bin']
    )
    
    account = get_account(web3, private_key)

    nonce = web3.eth.get_transaction_count(account.address)
    gas_price = round(float(web3.from_wei(web3.eth.gas_price, 'gwei')) * random_between(2.5, 2.7), 2)
    
    transaction = contract.constructor(100).build_transaction({
        'chainId': REDDIO_CHAIN_ID,       
        'gas': 1000000,        
        'gasPrice': web3.to_wei(gas_price, 'gwei'),       
        'nonce': nonce,    
        })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"account {account.address} has been deployed contract {receipt.contractAddress}")
    return receipt.contractAddress
