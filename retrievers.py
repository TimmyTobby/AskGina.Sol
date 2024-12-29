from langchain_community.document_loaders import CSVLoader, PyPDFLoader, WebBaseLoader
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
import requests
from langchain.schema import Document
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pickle

# ## Satic Retriever
# urls = [
#     "https://solana.com/docs",
#     "https://solana.com/docs/intro/installation",
#     "https://solana.com/docs/intro/quick-start",
#     "https://solana.com/docs/intro/quick-start/reading-from-network",
#     "https://solana.com/docs/intro/quick-start/writing-to-network",
#     "https://solana.com/docs/intro/quick-start/cross-program-invocation",
#     "https://solana.com/docs/intro/quick-start/deploying-programs",
#     "https://solana.com/docs/intro/quick-start/program-derived-address",
#     "https://solana.com/docs/intro/wallets",
#     "https://solana.com/docs/core/tokens",
#     "https://solana.com/docs/terminology",
#     "https://solana.com/docs/rpc",
#     "https://solana.com/docs/rpc/http",
#     "https://solana.com/docs/core/clusters",  # Solana network clusters and public RPC endpoints
#     "https://solana.com/docs/programs/anchor",  # Anchor framework guide
#     "https://solana.com/docs/core/validator",  # Running a Solana validator node
#     "https://solana.com/docs/core/staking",  # Solana staking guide
#     "https://solana.com/docs/core/vote",  # Voting mechanics on Solana
#     "https://solana.com/docs/core/epoch",  # Epoch and leader schedule
#     "https://solana.com/docs/core/ledger",  # Solana ledger and storage
#     "https://solana.com/docs/core/transactions",  # Detailed explanation of Solana transactions
#     "https://solana.com/docs/core/accounts",  # Understanding accounts on Solana
#     "https://solana.com/docs/core/rewards",  # Rewards structure in Solana
#     "https://solana.com/docs/core/performance",  # Solana's performance and scaling
#     "https://solana.com/docs/core/serialization",  # Serialization formats in Solana
#     "https://solana.com/docs/core/runtime",  # Solana runtime and program execution
#     "https://solana.com/docs/integrations/exchange",  # Exchange integrations with Solana
#     "https://solana.com/docs/integrations/wallet",  # Wallet integrations on Solana
#     "https://solana.com/docs/integrations/oracles",  # Using oracles with Solana
#     "https://solana.com/docs/integrations/dex",  # Decentralized exchanges (DEX) on Solana
#     "https://solana.com/docs/integrations/nft",  # Non-fungible tokens (NFTs) on Solana
#     "https://solana.com/docs/integrations/defi",  # Decentralized finance (DeFi) on Solana
#     "https://solana.com/docs/cli",  # Solana Command Line Interface (CLI) guide
#     "https://solana.com/docs/explorer",  # Using the Solana Explorer
#     "https://solana.com/docs/test-validator",  # Setting up a local test validator
#     "https://solana.com/docs/sysvar",  # Understanding system variables in Solana
#     "https://solana.com/docs/serialization/jsonrpc-api",  # JSON-RPC API details
#     "https://solana.com/docs/security-model" # Solana's security model and principles
# ]
# docs = [WebBaseLoader(url).load() for url in urls] 
# docs_list = [item for sublist in docs for item in sublist]

# # Processing the documents
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#     chunk_size=1000, chunk_overlap=200
# )
# doc_splits = text_splitter.split_documents(docs_list)
with open(r"C:\Users\HP\Desktop\LLM Bootcamp\SuperteamNG_30Days_LLM_Bootcamp\Notebooks\embedding_model.pkl", 'rb') as f:
    embedding_model = pickle.load(f)


# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="arag-chroma",
#     embedding=embedding_model,
#     persist_directory= "askgina_db"
# )
# # Save to disk
# vectorstore.persist()

# Reload the persisted vectorstore from the directory
vectorstore = Chroma(
    collection_name="arag-chroma",
    embedding_function=embedding_model,
    persist_directory="askgina_db"
)


retriever = vectorstore.as_retriever()



# ## DYNAMIC RETRIEVER 
# QuickNode Endpoint URL (replace with your endpoint)
# QUICKNODE_URL = "https://frequent-muddy-tab.solana-mainnet.quiknode.pro/2c92262b06f6ab2361407f2df8ad92ab5adc7b61"

# # Load the embedding model
# # with open(r"C:\Users\HP\Desktop\LLM Bootcamp\SuperteamNG_30Days_LLM_Bootcamp\Notebooks\embedding_model.pkl", 'rb') as f:
# #     embedding_model = pickle.load(f)

# # Function to get the latest slot number
# def get_latest_slot():
#     payload = {
#         "jsonrpc": "2.0",
#         "id": 1,
#         "method": "getSlot",
#         "params": []
#     }
#     response = requests.post(QUICKNODE_URL, json=payload)
#     if response.status_code == 200:
#         return response.json()["result"]
#     else:
#         print(f"Error fetching latest slot: {response.text}")
#         return None
    
def get_solana_price():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data["solana"]["usd"]
    except Exception as e:
        print(f"Error fetching Solana price: {e}")
        return None 

def load_data():
    # Loading data from the QuickNode Streams stored data
    with open("latest_block.json", "r") as file:
        data = json.load(file)
    return data

def create_realtime_retriever_2():
    # Load the data into the retriever
    data = load_data()
# Now you can use the `data` variable
    block_data = data.get("data", [])[0]
    current_price = get_solana_price()
    no_transactions = len(block_data['transactions'])
    latest_transaction = block_data['transactions'][0]
    filtered_block_data = {'nunmber_transactions' : no_transactions,
                           'solana_current_price' : current_price,
                        #    'slot' : latest_slot,
                           'latest_transaction' : latest_transaction}
    for key, value in block_data.items():
        filtered_block_data[key] = value
        if key == "transactions":
            break
        # print(f"Key: {key}, Value: {value}")
        page_content = json.dumps(filtered_block_data, indent=2) 
        metadata = {
            "block_height": block_data.get("blockHeight"),
            "block_time": block_data.get("blockTime"),
            'nunmber_transactions' : no_transactions,
            'solana_current_price' : current_price,
            # 'slot' : latest_slot
            'latest_transaction' : latest_transaction,
            "block_hash": block_data.get("blockhash")
        }
        documents = [
            Document(
                page_content=page_content,  
                metadata=metadata
            )
        ]
    return documents




















# # Function to fetch block data for a specific slot
# def get_block_data(slot):
#     payload = {
#         "jsonrpc": "2.0",
#         "id": 1,
#         "method": "getBlock",
#         "params": [
#             slot,
#             {
#                 "encoding": "json",
#                 "transactionDetails": "full",
#                 "rewards": False,
#                 "maxSupportedTransactionVersion": 0  # Add this parameter
#             }
#         ]
#     }
#     headers = {"Content-Type": "application/json"}

#     # Send request to QuickNode
#     response = requests.post(QUICKNODE_URL, headers=headers, json=payload)

#     if response.status_code == 200:
#         if "result" in response.json() and response.json()["result"] is not None:
#             print(f"Successfully fetched data for slot {slot}")
#             return response.json()["result"]
#         else:
#             print(f"No data found for slot {slot}")
#             return None
#     else:
#         print(f"Error fetching data for slot {slot}: {response.status_code}")
#         print(response.json())
#         return None

# # Function to create a retriever for real-time block data
# def create_realtime_retriever():
#     latest_slot = get_latest_slot()
#     if latest_slot:
#         # print(f"Latest slot: {latest_slot}")
#         block_data = get_block_data(latest_slot)
#         # print(type(block_data))

#     current_price = get_solana_price()
#     no_transactions = len(block_data['transactions'])
#     latest_transaction = block_data['transactions'][0]
#     filtered_block_data = {'nunmber_transactions' : no_transactions,
#                            'solana_current_price' : current_price,
#                            'slot' : latest_slot,
#                            'latest_transaction' : latest_transaction}
#     for key, value in block_data.items():
#         filtered_block_data[key] = value
#         if key == "transactions":
#             break
#         # print(f"Key: {key}, Value: {value}")
#         page_content = json.dumps(filtered_block_data, indent=2)  # Serialize dictionary to JSON string
#         metadata = {
#             "block_height": block_data.get("blockHeight"),
#             "block_time": block_data.get("blockTime"),
#             'nunmber_transactions' : no_transactions,
#             'solana_current_price' : current_price,
#             'slot' : latest_slot,
#             'latest_transaction' : latest_transaction,
#             "block_hash": block_data.get("blockhash")
#         }
#         documents = [
#             Document(
#                 page_content=page_content,  # Pass the stringified content
#                 metadata=metadata  # Pass metadata
#             )
#         ]
#     return documents


# # QuickNode Endpoint URL (replace with your endpoint)
# QUICKNODE_URL = "https://frequent-muddy-tab.solana-mainnet.quiknode.pro/2c92262b06f6ab2361407f2df8ad92ab5adc7b61"

# # Load the embedding model
# # with open(r"C:\Users\HP\Desktop\LLM Bootcamp\SuperteamNG_30Days_LLM_Bootcamp\Notebooks\embedding_model.pkl", 'rb') as f:
# #     embedding_model = pickle.load(f)

# # Function to get the latest slot number
# def get_latest_slot():
#     payload = {
#         "jsonrpc": "2.0",
#         "id": 1,
#         "method": "getSlot",
#         "params": []
#     }
#     response = requests.post(QUICKNODE_URL, json=payload)
#     if response.status_code == 200:
#         return response.json()["result"]
#     else:
#         print(f"Error fetching latest slot: {response.text}")
#         return None

# # Function to fetch block data for a specific slot
# def get_block_data(slot):
#     payload = {
#         "jsonrpc": "2.0",
#         "id": 1,
#         "method": "getBlock",
#         "params": [
#             slot,
#             {
#                 "encoding": "json",
#                 "transactionDetails": "full",
#                 "rewards": False,
#                 "maxSupportedTransactionVersion": 0  # Add this parameter
#             }
#         ]
#     }
#     headers = {"Content-Type": "application/json"}

#     # Send request to QuickNode
#     response = requests.post(QUICKNODE_URL, headers=headers, json=payload)

#     if response.status_code == 200:
#         if "result" in response.json() and response.json()["result"] is not None:
#             print(f"Successfully fetched data for slot {slot}")
#             return response.json()["result"]
#         else:
#             print(f"No data found for slot {slot}")
#             return None
#     else:
#         print(f"Error fetching data for slot {slot}: {response.status_code}")
#         print(response.json())
#         return None

# # Function to create a retriever for real-time block data
# def create_realtime_retriever(embedding_model):
#     latest_slot = get_latest_slot()
#     if latest_slot:
#         # print(f"Latest slot: {latest_slot}")
#         block_data = get_block_data(latest_slot)
#         # print(type(block_data))

#     no_transactions = len(block_data['transactions'])
#     filtered_block_data = {}
#     for key, value in block_data.items():
#         filtered_block_data[key] = value
#         if key == "transactions":
#             break
#         # print(f"Key: {key}, Value: {value}")
#         page_content = json.dumps(filtered_block_data, indent=2)  # Serialize dictionary to JSON string
#         metadata = {
#             "block_height": block_data.get("blockHeight"),
#             "block_time": block_data.get("blockTime"),
#             'number_of_transactions' : no_transactions,
#             'slot_number' : latest_slot,
#             "block_hash": block_data.get("blockhash")
#         }
#         documents = [
#             Document(
#                 page_content=page_content,  # Pass the stringified content
#                 metadata=metadata  # Pass metadata
#             )
#         ]
#     # Chunk the block data
#     text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#         chunk_size=1000, chunk_overlap=200
#     )
#     doc_splits = text_splitter.split_documents(documents)

#     # Create an in-memory vectorstore
#     vectorstore = Chroma.from_documents(
#         documents=doc_splits,
#         embedding=embedding_model,
#     )
#     return vectorstore.as_retriever()

# realtime_retriever = create_realtime_retriever(embedding_model)
# # Main script to fetch and query real-time data
# if __name__ == "__main__":
#     # # Fetch the latest slot and block data
#     # latest_slot = get_latest_slot()
#     # if latest_slot:
#     #     print(f"Latest slot: {latest_slot}")
#     #     block_data = get_block_data(latest_slot)
#     #     print(type(block_data))
#     #     if block_data:
#     #         # Create a retriever for the real-time data
#     #         realtime_retriever = create_realtime_retriever(block_data, embedding_model) 
            
#             # Example query
#             query = "What is the current blockhash?"
#             realtime_results = realtime_retriever.invoke(query, n_result = 1)
            
#             # Display results
#             print("\nQuery Results:")
#             for res in realtime_results:
#                 print(res)