from web3 import Web3
import json
import config
import time
import data

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

address = {
    # pancakeswapv2 router
    "panRouterContractAddress": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    # Your Wallet Address
    "sender_address": input("Enter your Wallet address : "),
    # WBNB contract address
    "wbnb_address": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"
}


def connect():
    if web3.isConnected():
        print("Connected")
    else:
        print("Cannot Connect")
        quit()


def sell():

    # Get BNB Balance
    balance = web3.eth.get_balance(address["sender_address"])
    humanReadable = web3.fromWei(balance, 'ether')
    print(humanReadable)

    # Contract id is the new token we are swaping to
    contract_id = web3.toChecksumAddress(
        input("Enter the Contract Address of token you want to sell: "))

    # Setup the PancakeSwap contract
    contract = web3.eth.contract(
        address=address["panRouterContractAddress"], abi=data.panabi)

    # Create token Instance for Token
    sellTokenContract = web3.eth.contract(contract_id, abi=data.sellAbi)

    # Get Token Balance
    balance = sellTokenContract.functions.balanceOf(
        address["sender_address"]).call()
    symbol = sellTokenContract.functions.symbol().call()
    readable = web3.fromWei(balance, 'ether')
    print("Balance: " + str(readable) + " " + symbol)

    # Enter amount of token to sell
    tokenValue = web3.toWei(
        input("Enter amount of " + symbol + " you want to sell: "), 'ether')

    # Approve Token before Selling
    tokenValue2 = web3.fromWei(tokenValue, 'ether')
    start = time.time()
    approve = sellTokenContract.functions.approve(address["panRouterContractAddress"], balance).buildTransaction({
        'from': address["sender_address"],
        'gasPrice': web3.toWei('5', 'gwei'),
        'nonce': web3.eth.get_transaction_count(address=["sender_address"]),
    })

    signed_txn = web3.eth.account.sign_transaction(
        approve, private_key=config.private)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Approved: " + web3.toHex(tx_token))

    # Wait after approve 10 seconds before sending transaction
    time.sleep(10)
    print(f"Swapping {tokenValue2} {symbol} for BNB")
    # Swaping exact Token for ETH

    pancakeswap2_txn = contract.functions.swapExactTokensForETH(
        tokenValue, 0,
        [contract_id, web3.toChecksumAddress(address["wbnb_address"])],
        sender_address,
        (int(time.time()) + 1000000)

    ).buildTransaction({
        'from': sender_address,
        'gasPrice': web3.toWei('5', 'gwei'),
        'nonce': web3.eth.get_transaction_count(address["sender_address"]),
    })

    signed_txn = web3.eth.account.sign_transaction(
        pancakeswap2_txn, private_key=config.private)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Sold {symbol}: " + web3.toHex(tx_token))


if __name__ == "__main__":
    connect()
    sell()
