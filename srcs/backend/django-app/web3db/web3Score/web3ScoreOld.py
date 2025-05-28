from django.conf import settings
from .util import JsonFile
from web3 import Web3
import threading
import asyncio
import solcx
import json
import os
import sys
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

class Web3ScoreManager():
    _web3Score = None

    def __init__(self, web3Provider, jsonPath) -> None:
        self.web3 = Web3(web3Provider) 
        self.data = JsonFile(os.path.join(settings.BASE_DIR, jsonPath))
        self.status = "starting"
        if not self.web3.is_connected():
            raise RuntimeError("Cant connect to testnet!")

    def loadup(self):
        if self.status != "starting":
            return
        self.status = "init"
        if self.data.fileExists():
            self.data.load()
            self.account = self.web3.eth.account.from_key(self.data["privateKey"])
        else:
            self.account = self.web3.eth.account.create()
            self.data.data = {
                "privateKey": self.web3.to_hex(self.account.key), 
                "smartContract": None, 
                "bin": None, 
                "abi": None 
                }
            self.data.save()
        logger.warning(f"Account address: { self.account.address }")
        self.createSmartContract()

    def createSmartContract(self):
        if self.data["smartContract"] is not None:
            self.onDeploy()
            return bytes(0)
        if self.data["bin"] is None or self.data["abi"] is None:
            self.compileSmartContract()
            #try:
            #except:
            #    logger.warning("Error compiling smart contract")
            #    return False
        return asyncio.run(self.deploySmartContract())

    def onDeploy(self):
        self.contract = self.getSmartContractWeb3Instance()
        self.web3.eth.default_account = self.account.address
        self.status = "deployed"
        logger.warning(f"Contract deployed at { self.data["smartContract"] }")

    def compileSmartContract(self):
        solcx.install_solc('0.7.0')
        compiled = solcx.compile_files(
            [f"{settings.BASE_DIR}/web3db/smartContract.sol"],
            output_values=["abi", "bin"],
            solc_version="0.7.0"
        )
        contract_id, contract_interface = compiled.popitem()
        self.data["bin"] = contract_interface["bin"]
        self.data["abi"] = contract_interface["abi"]
        self.data.save()

    #def deploySmartContract(self):
    #    contract = self.web3.eth.contract(abi=self.data["abi"], bytecode=self.data["bin"])
    #    self.status = "deploying"
#
    #    nonce = self.web3.eth.get_transaction_count(self.account.address)
    #    transaction = contract.constructor().build_transaction({
	#		"chainId":  self.web3.eth.chain_id,
    #        "gasPrice":  self.web3.eth.gas_price,
	#		"from": self.account.address,
	#		"nonce": nonce,
    #    })
    #    signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.account.key)
    #    tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
#
    #    thread = threading.Thread(target=self.waitForSmarContractConfirmation, args=(tx_hash, ))
    #    thread.start()
    #    return tx_hash

    async def deploySmartContract(self):
        contract = self.web3.eth.contract(abi=self.data["abi"], bytecode=self.data["bin"])
        self.status = "deploying"

        nonce = self.web3.eth.get_transaction_count(self.account.address)
        transaction = contract.constructor().build_transaction({
			"chainId":  self.web3.eth.chain_id,
            "gasPrice":  self.web3.eth.gas_price,
			"from": self.account.address,
			"nonce": nonce,
        })
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        asyncio.create_task(self.waitForSmarContractConfirmation(tx_hash))
        return tx_hash

    async def waitForSmarContractConfirmation(self, tx_hash):
        logger.warning(f"Contract deploying - TX: { self.web3.to_hex(tx_hash) }")
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        self.data["smartContract"] = tx_receipt.contractAddress
        self.data.save()
        self.onDeploy()

    def getSmartContractWeb3Instance(self):
        return self.web3.eth.contract(
            address=self.data["smartContract"],
            abi=self.data["abi"]
        )

    def setTournamentScore(self, tournamentId, score):
        if self.status != "deployed":
            return
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        transaction = self.contract.functions.setScore(tournamentId, json.dumps(score)).build_transaction({
            "chainId":  self.web3.eth.chain_id,
            "from": self.account.address,
            "nonce": nonce,
        })
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.account.key)
        tx_hash = self.web3.to_hex(self.web3.eth.send_raw_transaction(signed_txn.rawTransaction))
        logger.warning(f"Setting tournament score - TX: { tx_hash }")
        return tx_hash

    def getTournamentScore(self, tournamentId):
        if self.status != "deployed":
            return
        score = self.contract.functions.getScore(tournamentId).call()
        if len(score) < 1:
            return { "success": False }
        return { "success": True, "score": json.loads(score)}

    def getInstance():
        if Web3ScoreManager._web3Score is None:
            Web3ScoreManager._web3Score = Web3ScoreManager(
                Web3.HTTPProvider("https://rpc.ankr.com/eth_sepolia"), # Web3.EthereumTesterProvider()
                'web3db/smartContract.json'
            )
            Web3ScoreManager._web3Score.loadup()
        return Web3ScoreManager._web3Score

def _start():
    if "backend.asgi:application" not in sys.argv:
        if "runserver" not in sys.argv:
                return
    logger.warning(f"Running ")
    Web3ScoreManager.getInstance()
    
_start()