import streamlit as st
import hashlib
import datetime
import json
import os

# Define the Block class
class Block:
    def __init__(self, index, data, timestamp, previous_hash):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'data': self.data,
            'timestamp': str(self.timestamp),
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# Define the Blockchain class
class LibraryBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        genesis_data = {
            'book_title': 'Genesis Book',
            'borrower': 'Library',
            'date_issued': str(datetime.datetime.now())
        }
        return Block(0, genesis_data, datetime.datetime.now(), '0')

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest = self.get_latest_block()
        new_block = Block(
            index=latest.index + 1,
            data=data,
            timestamp=datetime.datetime.now(),
            previous_hash=latest.hash
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.calculate_hash():
                return False

            if curr.previous_hash != prev.hash:
                return False

        return True

# Save blockchain to a file (JSON)
def save_blockchain(chain, filename="blockchain_data.json"):
    with open(filename, "w") as f:
        json.dump([{
            "index": b.index,
            "data": b.data,
            "timestamp": str(b.timestamp),
            "previous_hash": b.previous_hash,
            "hash": b.hash
        } for b in chain], f, indent=4)

# Load blockchain from a file (JSON)
def load_blockchain(filename="blockchain_data.json"):
    if not os.path.exists(filename):
        return LibraryBlockchain()  # return genesis block if file doesn't exist

    with open(filename, "r") as f:
        data = json.load(f)
        blockchain = LibraryBlockchain()
        blockchain.chain = []
        for block_data in data:
            block = Block(
                index=block_data['index'],
                data=block_data['data'],
                timestamp=block_data['timestamp'],
                previous_hash=block_data['previous_hash']
            )
            block.hash = block_data['hash']  # restore hash directly
            blockchain.chain.append(block)
        return blockchain

# Initialize blockchain (stored in session state)
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = load_blockchain()

st.title("📚 Library Book Issuing Ledger using Blockchain")

# Sidebar to issue a new book
st.sidebar.header("📘 Issue New Book")
with st.sidebar.form("issue_form"):
    book_title = st.text_input("Book Title")
    borrower = st.text_input("Borrower's Name")
    date_issued = st.date_input("Date Issued", datetime.date.today())
    submitted = st.form_submit_button("Issue Book")

    if submitted:
        if book_title and borrower:
            new_data = {
                'book_title': book_title,
                'borrower': borrower,
                'date_issued': str(date_issued)
            }
            st.session_state.blockchain.add_block(new_data)
            save_blockchain(st.session_state.blockchain.chain)  # Save the blockchain data after adding the new block
            st.success(f"Book '{book_title}' issued to {borrower}.")
        else:
            st.error("Please fill in both the book title and borrower's name.")

# Display the blockchain ledger
st.header("📜 Blockchain Ledger")
for block in st.session_state.blockchain.chain:
    with st.expander(f"Block {block.index}"):
        st.write("**Timestamp:**", block.timestamp)
        st.write("**Book Title:**", block.data['book_title'])
        st.write("**Borrower:**", block.data['borrower'])
        st.write("**Date Issued:**", block.data['date_issued'])
        st.write("**Hash:**", block.hash)
        st.write("**Previous Hash:**", block.previous_hash)

# Validate the blockchain
st.header("🔐 Blockchain Validation")
if st.session_state.blockchain.is_chain_valid():
    st.success("✅ Blockchain is valid.")
else:
    st.error("❌ Blockchain is invalid!")
