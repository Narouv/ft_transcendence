from .util import JsonFile
from django.conf import settings
from web3 import Web3
import solcx
import json
import os
import logging

logger = logging.getLogger(__name__)

class Web3ContractFactory():
	def __init__(self, web3Provider) -> None:
		if "ETH_PK" not in os.environ:
			raise "No Private-Key specified!"
		self.web3 = Web3(web3Provider) 
		self.account = self.web3.eth.account.from_key(os.environ["ETH_PK"])

	def compileSolidityContract(self, path):
		solcx.install_solc('0.7.0')
		compiled = solcx.compile_files(
			[os.path.join(settings.BASE_DIR, path)],
			output_values=["abi", "bin"],
			solc_version="0.7.0"
		)
		contract_id, contract_interface = compiled.popitem()
		contractData = {}
		contractData["bin"] = contract_interface["bin"]
		contractData["abi"] = contract_interface["abi"]
		contractData["id"] = contract_id
		return contractData
	
	def deploySmartContract(self, contractData):
		nonce = self.web3.eth.get_transaction_count(self.account.address)
		contract = self.web3.eth.contract(abi=contractData["abi"], bytecode=contractData["bin"])
		transaction = contract.constructor().build_transaction({
			"chainId":  self.web3.eth.chain_id,
			"gasPrice":  self.web3.eth.gas_price,
			"from": self.account.address,
			"nonce": nonce,
		})
		signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.account.key)
		tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
		logger.warning(f"[DEPLOYING] - Waiting for confirmation - TX: { self.web3.to_hex(tx_hash) }")
		tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
		return { "tx": tx_hash, "address": tx_receipt.contractAddress }
	
	def createContract(self, solFile, outFile):
		contractData = self.compileSolidityContract(solFile)
		deployedContractData = self.deploySmartContract(contractData)
		resultFile = JsonFile(os.path.join(settings.BASE_DIR, outFile))
		resultFile['bin'] = contractData['bin']
		resultFile['abi'] = contractData['abi']
		resultFile['address'] = deployedContractData['address']
		resultFile.save()
		logger.warning(f"Done saved in {outFile}")

class Web3ContractManager(Web3ContractFactory):
	def __init__(self, web3Provider,contractFile) -> None:
		super().__init__(web3Provider)
		self.contract = None
		if not self.loadContract(contractFile):
			raise "No Valid Contract file specified!"

	def loadContract(self, path):
		file = JsonFile(os.path.join(settings.BASE_DIR, path))
		if not file.fileExists():
			return False
		file.load()
		self.contract = self.web3.eth.contract(
			address=file["address"],
			abi=file["abi"]
		)
		return True

class Web3TournamentScore(Web3ContractManager):
	_web3Score = None
	
	def __init__(self, web3Provider, contractFile) -> None:
		super().__init__(web3Provider, contractFile)

	def getTournamentScore(self, tournamentId):
		if not self.contract:
			return False
		score = self.contract.functions.getScore(tournamentId).call()
		if len(score) < 1:
			return { "success": False }
		return { "success": True, "score": json.loads(score)}

	def setTournamentScore(self, tournamentId, score):
		if not self.contract:
			return False
		nonce = self.web3.eth.get_transaction_count(self.account.address)
		transaction = self.contract.functions.setScore(tournamentId, json.dumps(score)).build_transaction({
			"chainId":  self.web3.eth.chain_id,
			"from": self.account.address,
			"nonce": nonce,
		})
		signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.account.key)
		tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
		logger.warning(f"Setting tournament score for {tournamentId} - TX: { self.web3.to_hex(tx_hash) }")
		return tx_hash
	
	def getInstance():
		if Web3TournamentScore._web3Score is None:
			Web3TournamentScore._web3Score = Web3TournamentScore(
				Web3.HTTPProvider("https://rpc.ankr.com/eth_sepolia"),
				'web3db/smartContractDeployed_1.json'
			)
		return Web3TournamentScore._web3Score

