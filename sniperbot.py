# import the following dependencies
import json
from web3 import Web3
import asyncio
import config
import time
import data


# add your blockchain connection information
bsc = 'https://bsc-dataseed.binance.org/'
web3 = Web3(Web3.HTTPProvider(bsc))

if web3.isConnected():
    print('Connected')
else:
    print('Cannot connect')

panRouterContractAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

contract = web3.eth.contract(
    address=data.uniswap_factory, abi=data.uniswap_factory_abi)


contractbuy = web3.eth.contract(
    address=panRouterContractAddress, abi=data.panabi)


wbnb = web3.toChecksumAddress(
    '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')  # WBNB
sender_address = web3.toChecksumAddress(
    '0xe8001AC529d3612B917fB90CBdd88B2d270789a7')  # the address which buys the token

balance = web3.eth.get_balance(sender_address)

humanReadable = web3.fromWei(balance, 'ether')
print("BNB Balance : ", humanReadable)

tokenToBuy = web3.toChecksumAddress(input("Enter Contract to buy : "))


# If conditions are met we buy the token
def buy():

    spend = web3.toChecksumAddress(
        "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # wbnb contract address

    nonce = web3.eth.get_transaction_count(sender_address)

    pancakeswap2_txn = contractbuy.functions.swapExactETHForTokens(
        0,  # set to 0, or specify minimum amount of token you want to receive - consider decimals!!!
        [spend, tokenToBuy],
        sender_address,
        (int(time.time()) + 10000)
    ).buildTransaction({
        'from': sender_address,
        # This is the Token(BNB) amount you want to Swap from
        'value': web3.toWei(0.1, 'ether'),
        'gasPrice': web3.toWei('5', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(
        pancakeswap2_txn, private_key=config.private)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Snipe was succesfull, bought: " + web3.toHex(tx_token))


# define function to handle events and print to the console
def handle_event(event):
    # print(Web3.toJSON(event))
    # and whatever
    pair = Web3.toJSON(event)

    print(pair)

    token0 = str(Web3.toJSON(event['args']['token1']))
    token1 = str(Web3.toJSON(event['args']['token0']))
    #block =  Web3.toJSON(event['blockNumber'])
    #txhash = Web3.toJSON(event['transactionHash'])
   # print("Block: " + block)
    #print("Txhash: " + txhash)
    print("Token0: " + token0)
    print("Token1: " + token1)

    wbnb2 = wbnb.upper()

    tokenToBuy2 = tokenToBuy.upper()

    if(token0.upper().strip('"') == wbnb2 and token1.upper().strip('"') == tokenToBuy2):
        print("pair detected")
        buy()
    elif(token0.upper().strip('"') == tokenToBuy2 and token1.upper().strip('"') == wbnb2):
        print("pair detected")
        buy()
    else:
        print("next pair")


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
        # log_loop(block_filter, 2),
        # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


main()
