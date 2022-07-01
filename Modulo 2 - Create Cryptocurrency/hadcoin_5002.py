import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')  # Create genesis block
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        # Build a new block
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,  # Proof of Work
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}

        # clean transaction list
        self.transactions = []

        # Add new block on chain
        self.chain.append(block)

        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            candidate_proof = str(new_proof ** 2 - previous_proof ** 2)  # Difficult level
            str_proof = candidate_proof.encode()  # Cast to String value
            hash_operation = hashlib.sha256(str_proof).hexdigest()  # Build a new hexadecimal hash

            if hash_operation[:4] == '0000':  # Problem solved
                check_proof = True
            else:
                new_proof += 1  # Increment new_proof to try another hash

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        # Get the first one to compare
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]

            # Check if chain is consistent
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # Check if proof is valid
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append( {'sender': sender,
                                   'receiver': receiver,
                                   'amount':amount})

        previous_block = self.get_previous_block()

        return previous_block['index'] + 1

# ************ DECENTRALIZED PART ************

    def add_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

    # Protocolo de Consenso
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False

# ******************************************************************


app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')


blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='Pedro', amount=1)

    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'Congrats, you mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}

    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid:
        response = {'message': 'Blockchain is valid!'}
    else:
        response = {'message': 'Blockchain is NOT valid!'}

    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json_param = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']

    if not all(key in json_param for key in transaction_keys):
        return 'Alguns elementos estão faltando', 400

    idx = blockchain.add_transaction(json_param['sender'], json_param['receiver'], json_param['amount'])
    response = {'message': f'Esta transacao sera adicionada ao bloco {idx}'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json_param = request.get_json()
    nodes = json_param.get('nodes')

    if nodes is None:
        return 'Nós inexistentes', 400

    for node in nodes:
        blockchain.add_node(node)

    response = {'message': 'Todos os nós foram conectados.',
                'total_nodes': list(blockchain.nodes)}

    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Cadeia substituida.',
                    'new_chain' : blockchain.chain}
    else:
        response = {'message': 'Cadeia mantida.',
                    'current_chain': blockchain.chain}

    return jsonify(response), 201



app.run(host='127.0.0.1', port=5002)