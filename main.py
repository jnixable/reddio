import time
from core.config import BRIDGE_CONTRACT_ABI, BRIDGE_CONTRACT_ADDRESS, REDDIO_DEPLOY_CONTRACT, REDDIO_RPC_URL, REDDIO_COIN_NAME, SEPOLIA_CHAIN_ID, SEPOLIA_RPC_URL
from core.contract import deploy_contract
from core.utils import connect_to_web3, generate_random_name, get_account, random_between, retry



def send_eth(private_key, amount): 
  
  web3 = connect_to_web3(REDDIO_RPC_URL)
  account = get_account(web3, private_key)
  
  balance_wei = web3.eth.get_balance(account.address)
  balance_eth = web3.from_wei(balance_wei, 'ether')
  print(f"Balance of {account.address}: {balance_eth} {REDDIO_COIN_NAME}")
  
  nonce = web3.eth.get_transaction_count(account.address)
  print(f"nonce of {account.address}: {nonce}")
  
  tx = {
    'nonce': nonce,
    'to': account.address,
    'value': web3.to_wei(amount, 'ether'),
    'gas': 1000000,
    'gasPrice': web3.to_wei(2.5, 'gwei')
  }
  
  signed_tx = web3.eth.account.sign_transaction(tx, private_key)
  tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
  
  print(web3.to_hex(tx_hash)) 
  
  time.sleep(3)
  
  receipt = retry(lambda: web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120), max_retries=5, wait_time=2)

  txStatus = "Success" if receipt.status == 1 else "Failed"
  print(f"Transaction hash: {receipt.transactionHash.hex()} ({txStatus})")
  
def bridge_eth(private_key, amount_eth):
  
  account = get_account(web3, private_key)
  print(f"Bridge {amount_eth} ETH from Sepolia to Reddio ({account.address})")
  
  web3 = connect_to_web3(SEPOLIA_RPC_URL)
  
  balance_wei = web3.eth.get_balance(account.address)
  balance_eth = web3.from_wei(balance_wei, 'ether')
  print(f"Balance of {account.address}: {balance_eth} ETH")
  
  nonce = web3.eth.get_transaction_count(account.address)
  
  contract = web3.eth.contract(address=BRIDGE_CONTRACT_ADDRESS, abi=BRIDGE_CONTRACT_ABI)
  
  recipient_address = account.address
  amount_in_wei = web3.to_wei(amount_eth, 'ether')
  escrow_fee = 3000000
  
  gas_price = round(float(web3.from_wei(web3.eth.gas_price, 'gwei')) * random_between(1.3, 1.4), 2) 

  tx = contract.functions.depositETH(
      recipient_address,
      amount_in_wei,
      escrow_fee
  ).build_transaction({
      'chainId': SEPOLIA_CHAIN_ID,
      'gas': 100000,
      'gasPrice': web3.to_wei(gas_price, 'gwei'),
      'nonce': nonce,
      'value': amount_in_wei, 
  })
  
  
  signed_tx = web3.eth.account.sign_transaction(tx, private_key)
  tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
  
  receipt = retry(lambda: web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120), max_retries=5, wait_time=2)
  
  txStatus = "Success" if receipt.status == 1 else "Failed"
  print(f"Transaction hash: {receipt.transactionHash.hex()} ({txStatus})")

if __name__ == "__main__":
  
  web3 = connect_to_web3(REDDIO_RPC_URL)
  
  with open('data/private_keys.txt') as f:
    private_keys = f.readlines()
    
  private_keys = [x.strip() for x in private_keys]
  
  for i, private_key in enumerate(private_keys):
    account = get_account(web3, private_key)
    send_amount = random_between(0.1, 1)
    print(f"Sending {send_amount} RED to {account.address}")
    send_eth(private_key, send_amount)
    bridge_amount = random_between(0.01, 0.02)
    bridge_eth(private_key, bridge_amount)
    if REDDIO_DEPLOY_CONTRACT == True:
      deploy_contract(private_key)
    print(f"______________{i}____________________\n")

  
  
  

