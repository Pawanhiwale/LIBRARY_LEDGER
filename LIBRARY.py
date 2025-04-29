import streamlit as st
import hashlib
import datetime
import json

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

# Define the Blockchain
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

# Initialize blockchain (stored in session)
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = LibraryBlockchain()

st.title("📚 Library Book Issuing Ledger using Blockchain")

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
            st.success(f"Book '{book_title}' issued to {borrower}.")
        else:
            st.error("Please fill in both the book title and borrower's name.")

st.header("📜 Blockchain Ledger")
for block in st.session_state.blockchain.chain:
    with st.expander(f"Block {block.index}"):
        st.write("**Timestamp:**", block.timestamp)
        st.write("**Book Title:**", block.data['book_title'])
        st.write("**Borrower:**", block.data['borrower'])
        st.write("**Date Issued:**", block.data['date_issued'])
        st.write("**Hash:**", block.hash)
        st.write("**Previous Hash:**", block.previous_hash)

# Validate blockchain
st.header("🔐 Blockchain Validation")
if st.session_state.blockchain.is_chain_valid():
    st.success("✅ Blockchain is valid.")
else:
    st.error("❌ Blockchain is invalid!")
