import requests
import time
from web3 import Web3
from loguru import logger
from eth_account import Account

from GenesisBox_config import GenesisBox_contract_address, receiveNFT_contract_address, GenesisBox_contract_abi, receiveNFT__contract__abi

logger.add('./log/runtime_{time}.log')
result_file = open('./result.txt', 'a+')
main_private_key = '0xxxx' #给箱子地址转gas的地址私钥
BEVM_rpc = 'https://rpc-mainnet-1.bevm.io'
web3 = Web3(Web3.HTTPProvider(BEVM_rpc))


def get_genesisBox_tokenid(address):
    """
        获取钱包的箱子编号
    """

    url = f'https://scan-mainnet-api.bevm.io/api/v2/tokens/0x09Ff8E49D0EA411A3422ed95E8f5497D4241F532/instances/?holder_address_hash={address}'
    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://runesairdrop.bevm.io',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://runesairdrop.bevm.io/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if 200 <= response.status_code < 300:
            tokenid = response.json()['items'][0]['id']
            logger.success(f'地址 {address} 获取的box tokenid为{tokenid}')
            return tokenid
        else:
            logger.warning(f'地址 {address} 获取box tokenid的请求返回异常 {response.content}')
            return
    except Exception as err:
        logger.error(f'地址 {address} 获取box tokenid的请求失败: {err}')
        return

def get_genesisbox_point(address):
    """
        查询打开箱子获得的积分数量
    """

    url = f"https://api.bevm.io/vote/address/info?address={address}"
    payload = {}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://runesairdrop.bevm.io',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://runesairdrop.bevm.io/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if 200 <= response.status_code < 300:
            genesisbox_point = response.json()['points']
            logger.success(f'地址 {address}  获得积分 {genesisbox_point}')
            result_file.write(f'地址 {address}  获得积分 {genesisbox_point}\n')
        else:
            logger.warning(f'地址 {address} 获取积分请求返回异常 {response.content}')
    except Exception as err:
        logger.error(f'{address}获取积分请求发送失败: {err}')

def genesisbox_approve(private_key, tokenid):
    """
        对箱子进行授权approve操作
    """

    if not tokenid:
        logger.error(f'地址 {address} 无tokenid 退出函数genesisbox_approve')
        return
    else:
        tokenid = int(tokenid)

    try:
        account = Account.from_key(private_key)
        get_balance_send_coin(account.address)    #获取地址余额并适当转gas

        GenesisBox_contract = web3.eth.contract(address=GenesisBox_contract_address, abi=GenesisBox_contract_abi)

        approve_tx = GenesisBox_contract.functions.approve(receiveNFT_contract_address, tokenid).build_transaction({
            'gas': 50000,  # 根据需要调整gas限制
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(account.address)
        })

        signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key=private_key)
        approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
        approve_receipt = web3.eth.wait_for_transaction_receipt(approve_tx_hash, timeout=120)
        logger.success(f"地址 {account.address} 的GenesisBox approve交易收据: {approve_receipt}")
    except Exception as err:
        logger.error(f'地址 {account.address} approve tx发送失败: {err}')

def receiceNFT(address, private_key, tokenid):
    """
        打开箱子
    """
    if not tokenid:
        logger.error(f'地址 {address} 无tokenid 退出函数genesisbox_approve')
        return
    from_address = address
    
    try:
        receiveNFT__contract = web3.eth.contract(address=receiveNFT_contract_address, abi=receiveNFT__contract__abi)
        receiveNFT_tx = receiveNFT__contract.functions.receiveNFT(int(tokenid)).build_transaction({
            'gas': 90000,  # 根据需要调整gas限制
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(from_address)
        })

        signed_receiveNFT_txn = web3.eth.account.sign_transaction(receiveNFT_tx, private_key)
        receiveNFT_tx_hash = web3.eth.send_raw_transaction(signed_receiveNFT_txn.rawTransaction)
        transfer_receipt = web3.eth.wait_for_transaction_receipt(receiveNFT_tx_hash, timeout=120)
        logger.success(f"地址 {address} GenesisBox receiveNFT收据: {transfer_receipt}")
    except Exception as err:
        logger.error(f'地址 {address} receiveNFT tx发送失败: {err}')

def get_balance_send_coin(address):
    """
        查询箱子地址的余额，判断是否需要转gas费
    """

    wei_balance = web3.eth.get_balance(address)
    btc_balance = web3.from_wei(wei_balance, 'ether')
    format_balance = "{:.8f}".format(btc_balance)
    logger.info(f'地址 {address} 余额{format_balance}')

    if float(format_balance) > 0.000007:
        logger.info(f'地址{address} 的余额大于0.000007,无需转gas')
        return

    from_address = Account.from_key(main_private_key).address
    to_address = address
    nonce = web3.eth.get_transaction_count(from_address)  # 在每次循环中动态获取最新的nonce值

    transaction = {
        'from': from_address,
        'to': to_address,
        'value': web3.to_wei(0.000007, 'ether'),
        'nonce': nonce,
        'gas': 21000,
        'gasPrice': web3.eth.gas_price
    }
    try:
        signed = web3.eth.account.sign_transaction(transaction, main_private_key)
        tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        logger.success(f"向地址 {address} 转账0.000007btc交易收据: {receipt}")

        return web3.eth.get_balance(address)
    except Exception as err:
        logger.error(f"向地址 {address} 转账0.000007btc失败: {err}")

if __name__ == "__main__":
    private_keys = []
    addresses = []
    with open('./keys.config', 'r', encoding='utf-8') as file:
        for line in file:
            private_key = line.strip()
            private_keys.append(private_key)

    for index, private_key in enumerate(private_keys):
        address = Account.from_key(private_key).address
        addresses.append(address)
        
        # print(f'private_key idx {index} key {private_key}')
        tokenid = get_genesisBox_tokenid(address)
        genesisbox_approve(private_key, tokenid)
        receiceNFT(address, private_key, tokenid)

    time.sleep(5)

    for index, address in enumerate(addresses):
        # print(f'addresses idx {index} key {address}')
        get_genesisbox_point(address)
        