from flask import Flask, render_template
from flask import request
import json
import requests
import hashlib as hasher
import datetime as date
node = Flask(__name__)


class Block:
  def __init__(self, index, timestamp, data, previous_hash):
    self.index = index
    self.timestamp = timestamp
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hash_block()
  
  def hash_block(self):
    sha = hasher.sha256()
    sha.update(str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash))
    return sha.hexdigest()

# Generate genesis block
def create_genesis_block():
  # Manually construct a block with
  # index zero and arbitrary previous hash
  return Block(0, date.datetime.now(), {
    "proof-of-work": 9,
    "transactions": None
  }, "0")

# A completely random address of the owner of this node
miner_address = "random-miner-address"
# This node's blockchain copy
blockchain = []
blockchain.append(create_genesis_block())
# Store the transactions that this node has in a list
this_nodes_transactions = []
# Store the url data of every
# other node in the network
# so that we can communicate
# with them
peer_nodes = ['http://192.168.43.57:5000']

mining = True

@node.route('/<name>')
def success(name):
   return render_template('%s.html' % name) 

@node.route('/txion', methods=['POST'])
def transaction():
  new_txion = {}
  new_txion["from"] = request.form["from"]
  new_txion["to"] = request.form["to"]
  new_txion["amount"] = request.form["amount"]
  this_nodes_transactions.append(new_txion)
  print "New transaction"
  print "FROM: {}".format(new_txion['from'].encode('ascii','replace'))
  print "TO: {}".format(new_txion['to'].encode('ascii','replace'))
  print "AMOUNT: {}\n".format(new_txion['amount'])
  # Then we let the client know it worked out
  return "Transaction submission successful\n"

@node.route('/blocks', methods=['GET'])
def get_blocks():
  chain_to_send = blockchain
  blocklist = ""
  for i in range(len(chain_to_send)):
    block = chain_to_send[i]
    block_index = str(block.index)
    block_timestamp = str(block.timestamp)
    block_data = str(block.data)
    block_hash = block.hash
#    assembled = json.dumps({
#    "index": block_index,
#    "timestamp": block_timestamp,
#    "data": block_data,
#    "hash": block_hash
#    })
    assembled = "index: " + block_index +',<br>' + "timestamp: " + block_timestamp +',<br>'+ "data: " + block_data+ ',<br>'+"hash: "+block_hash+'<br><br>'
    if blocklist == "":
      blocklist = assembled
    else:
      blocklist += assembled
  return blocklist

def find_new_chains():
  # Get the blockchains of every other node
  other_chains = []
  for node_url in peer_nodes:
    block = requests.get(node_url + "/blocks").content
    # Convert the JSON object to a Python dictionary
    #block = json.loads(block)
    block = str2dict(block)
    other_chains.append(block)
  return other_chains

def consensus():
  # Get the blocks from other nodes
  other_chains = find_new_chains()
  print(other_chains)
  # If our chain isn't longest,
  # then we store the longest chain
  longest_chain = blockchain
  for chain in other_chains:
    if len(longest_chain) < len(chain):
      longest_chain = chain
  return longest_chain

def proof_of_work(last_proof):
  incrementor = last_proof + 1
  while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
    incrementor += 1
  return incrementor

@node.route('/mine', methods = ['GET'])
def mine():
  blockchain = consensus()
  # Get the last proof of work
  last_block = blockchain[len(blockchain) - 1]
  last_proof = last_block.data['proof-of-work']
  proof = proof_of_work(last_proof)
  # we reward the miner by adding a transaction
  this_nodes_transactions.append(
    { "from": "network", "to": miner_address, "amount": 1 }
  )
  # Now we can gather the data needed
  # to create the new block
  new_block_data = {
    "proof-of-work": proof,
    "transactions": list(this_nodes_transactions)
  }
  new_block_index = last_block.index + 1
  new_block_timestamp = this_timestamp = date.datetime.now()
  last_block_hash = last_block.hash
  # Empty transaction list
  this_nodes_transactions[:] = []
  # Now create the
  # new block!
  mined_block = Block(
    new_block_index,
    new_block_timestamp,
    new_block_data,
    last_block_hash
  )
  blockchain.append(mined_block)
  # Let the client know we mined a block
  return "index: " + str(new_block_index) + ',<br>' +  "timestamp: " + str(new_block_timestamp) + ',<br>'  +  "data: " + str(new_block_data) + ',<br>'  +  "hash: " + last_block_hash + "<br>"

def str2dict(string):
    blocklist = []
    blocks = string.split('<br><br>')
    print(blocks)
    for block in blocks:
	if block in ['',' ','  ']:
		continue
	temp = {}
	attributes = block.split(',<br>')
	for attr in attributes:
	    values = attr.split(': ')
	    key = values[0]
	    value = values[1]
	    temp[key] = value       
	blocklist.append(temp)
    return blocklist

node.run(host='0.0.0.0')

