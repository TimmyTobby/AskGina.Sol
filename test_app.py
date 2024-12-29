import streamlit as st
from datetime import datetime
from askgina import graph

# Placeholder for your graph-based bot response function
def bot_response(user_input):
    """
    Mock bot response logic.
    Replace this with logic to query your compiled graph.
    """
    graph_input = {"question": user_input}
    final = None
    for event in graph.stream(graph_input, stream_mode="values"):
        final = event
    # Print the final event after the loop
    if final is not None:
        return final['generation'].content
    else:
        return ''

# Set up the app's layout
st.set_page_config(
    page_title="Gina: Solana Data Assistant",
    page_icon="💬",
    layout="wide"
)

# Sidebar content
with st.sidebar:
    st.title("Gina")
    st.markdown(
        """
        Welcome to **Gina**, your Solana on-chain data assistant!  
        Explore the blockchain effortlessly.  
        ---
        ### Features
        - Real-time query handling
        - Interactive chat interface
        - Powered by Langchain, QuickNode and graph intelligence
        ---
        **Need help?** Contact us!
        """
    )
    st.image("https://cdn.freelogovectors.net/wp-content/uploads/2023/01/solana_logo-freelogovectors.net_.png", use_container_width=True)

# Main app title and introduction
st.title("Gina: Your Solana On-Chain Data Assistant 💬")
st.subheader(
    """
    Welcome to Gina!  
    Interact with your personal assistant to explore Solana's on-chain data seamlessly.  
    **Ask any question** about the blockchain, and let Gina guide you.
    ---
    """
)

# session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input box for the user's message
st.markdown("### Chat Interface:")
user_input = st.text_input(
    "Type your message below:",
    key="user_input",
    help="Type your message and press Enter.",
    placeholder="e.g., What is the latest transaction on Solana?"
)

if user_input:
    # Append user message to chat history
    st.session_state.messages.append({"sender": "user", "message": user_input, "time": datetime.now()})

    # Get the bot's response based on the graph or logic
    response = bot_response(user_input)

    # Append bot's response to chat history
    st.session_state.messages.append({"sender": "AskGina", "message": response, "time": datetime.now()})

    # Clear the input field after a message is sent
    del st.session_state.user_input

# Display chat history with color-coded messages
st.markdown("---")
for msg in st.session_state.messages:
    if msg["sender"] == "user":
        st.markdown(
            f"<div style='background-color: #D4F1F4; padding: 10px; border-radius: 5px;'>"
            f"<strong>You:</strong> {msg['message']} <span style='font-size: 10px; color: gray;'>({msg['time'].strftime('%H:%M:%S')})</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background-color: #E8EAF6; padding: 10px; border-radius: 5px;'>"
            f"<strong>AskGina:</strong> {msg['message']} <span style='font-size: 10px; color: gray;'>({msg['time'].strftime('%H:%M:%S')})</span>"
            f"</div>",
            unsafe_allow_html=True
        )
st.markdown("---")

# Footer
st.markdown(
    """
    <div style='text-align: center; font-size: small;'>
        © 2024 Gina - Your Solana On-Chain Data Assistant. Powered by Langchain, QuickNode and graph intelligence
    </div>
    """,
    unsafe_allow_html=True
) 