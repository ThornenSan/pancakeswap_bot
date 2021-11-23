from web3 import Web3
import config
import time
import data


address = {
    # pancakeswapv2 router
    "panRouterContractAddress": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    # Your Wallet Address
    "sender_address": input("Enter your Wallet address : "),
    # WBNB contract address
    "wbnb_address": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"
}

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))


def connect():

    if web3.isConnected():
        print('Connected')
    else:
        print('Not Connected')
        quit()


def buy():
    # Check BNB Balance
    balance = web3.eth.get_balance(address["sender_address"])
    humanReadable = web3.fromWei(balance, 'ether')
    print("BNB Balance : ", humanReadable)
    buy_amount = int(input("Enter Amount of BNB for buying : "))

    # Contract Address of Token we want to buy
    tokenToBuy = web3.toChecksumAddress(input("Enter TokenAddress: "))
    spend = web3.toChecksumAddress(address["wbnb_address"])

    # Setup the PancakeSwap contract
    contract = web3.eth.contract(
        address=address.panRouterContractAddress, abi=data.panabi)
    nonce = web3.eth.get_transaction_count(address["sender_address"])

    pancakeswap2_txn = contract.functions.swapExactETHForTokens(
        0,
        [spend, tokenToBuy],
        address["sender_address"],
        (int(time.time()) + 10000)
    ).buildTransaction({
        'from': address["sender_address"],
        'value': web3.toWei(buy_amount, 'ether'),
        'gasPrice': web3.toWei('5', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(
        pancakeswap2_txn, private_key=config.private)

    try:
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("Bought Successfully")
        print("Tx_token : ", web3.toHex(tx_token))

    except ValueError as e:
        if e.args[0].get('message') in 'intrinsic gas too low':
            result = ["Failed", f"ERROR: {e.args[0].get('message')}"]
        else:
            result = [
                "Failed", f"ERROR: {e.args[0].get('message')} : {e.args[0].get('code')}"]
        print(result)


if __name__ == "__main__":
    connect()
    buy()
