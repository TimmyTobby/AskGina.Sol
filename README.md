<<<<<<< HEAD
<img src="AskGina_AI_Brain_Logo copy.jpeg" alt="alt text" width="400" height="400"/>

# Ask Gina Alt for Solana
## AI-Powered in-feed assistant on Solana to help with on-chain data
### Overview

Ask Gina alt for Solana is an AI-powered in-feed assistant designed to streamline access to on-chain data for the Solana blockchain network. Positioned under the "Social and Chat Agents" category, it offers a seamless way for users to interact with and retrieve blockchain information.

### Purpose

The primary purpose of Ask Gina alt is to provide a user-friendly and efficient mechanism for querying and understanding Solana’s blockchain data. By leveraging artificial intelligence, this assistant aims to:

- Simplify access to complex on-chain data.

- Enhance the user experience for both technical and non-technical audiences.

- Support blockchain-based workflows by delivering relevant insights.

### Features

1. **AI-Powered Assistance**

    - Utilizes advanced machine learning models to provide accurate and timely responses.

2. **Real-Time On-Chain Data**

    - Offers insights into real-time data such as block details, transactions, and other relevant blockchain metrics.

3. **Integration with Solana Ecosystem**

    - Tailored to work seamlessly with Solana’s infrastructure, ensuring precise and context-aware responses.

### Use Cases

- **Blockchain Analytics:** Retrieve information on blocks, transactions, and other key metrics.

- **User Support:** Assist users with common Solana-related queries in a conversational format.

- **Development Aid:** Aid developers working on Solana-based projects by providing easy access to technical data.

## How to set it up

1. **Create a stream on QuickNode**  
   - First, create a Stream on QuickNode and set the destination to the webhook route you created on your flask app.  
   - This allows you to send data from the stream to your endpoint for processing.

2. **Host the Webhook**  
   - Host the webhook on a server or cloud provider, ensuring it can accept incoming POST requests.
   - You can use a simple web framework like I did using Flask to handle these requests and exposing it to the internet using ngrok so it can receive data from QuickNode.

3. **Configure Webhook to Handle Data**  
   - Set up the Flask app/webhook to process the incoming data and interact with the rest of the application logic, such as calling APIs or invoking Gina. 

4. **Integrate with AskGina's brain which is the compiled graph**  
   - Connect the webhook to AskGina's brain (graph) to process the data and generate responses.

5. **Testing**  
   - Deploying and testing the server and the flow to confirm that data from QuickNode Streams is being received and processed correctly using streamlit the `test_app.py`.
   - You may also want to monitor the server for any issues, especially during initial tests.

