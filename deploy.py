import json
from random import paretovariate
from brownie import Contract
from solcx import compile_standard
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    #print(simple_storage_file)

#compile solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        }
    },
    solc_version="0.6.0",
)
#print(compiled_sol)
with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

#get bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
#print(abi)

#for connecting to GANACHE
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/1aa1e0cc411844b79625b2f0b4369de3"))
chain_id = 4
my_address = "0x92b2129E6701a9b3F8AB7714CEF3edAd86a45b0a"
#Get private key from enivonment variables: 
private_key = os.getenv("PRIVATE_KEY")
#print(private_key)
#never hardcode private key & also in environment variable
#brownie has better private key management
#always prefix 0x in private key while using python

#create the contract in python(contarct object)
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
#print(SimpleStorage)

#latest no. of transactions used as nonce
#get the latest transaction

nonce = w3.eth.getTransactionCount(my_address)
#print(nonce)
#1Build the contact deploy transaction
#2sign the transaction
#3send the transaction
transaction = SimpleStorage.constructor().buildTransaction({"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce})
#print(transaction)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
#print(signed_txn)
#send this signed transaction
print("Deploying contract...")
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
#block cofirmation
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print("Deployed!")

#working with contract
#need contact address & abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
#initial value of fav. no.
print(simple_storage.functions.retrieve().call())
#print(simple_storage.functions.store(15).call())
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1
})
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receiptv = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print(simple_storage.functions.retrieve().call())