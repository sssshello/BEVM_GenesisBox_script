from eth_account import Account
from web3 import Web3

"""
    根据助记词派生出多个钱包地址
"""
BEVM_rpc = 'https://rpc-mainnet-1.bevm.io'
web3 = Web3(Web3.HTTPProvider(BEVM_rpc))
Account.enable_unaudited_hdwallet_features()

keys_file = open('./keys.config', 'a+')

mymnemonic = ''     #助记词

for i in range(0, 100):
    path = f"m/44'/60'/0'/0/{i}"
    account = Account.from_mnemonic(mymnemonic, account_path = path)
    i = i + 1
    print(f'序号{i} 地址 {account.address} 私钥 {account.key.hex()}')
    keys_file.write(f'{account.key.hex()}\n')       #将生成的地址私钥存入文件中
