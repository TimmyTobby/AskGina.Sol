import os
from flask import Flask, request, Response
import json

app2 = Flask(__name__)
@app2.route('/webhook', methods=['POST'])
def webhook():
    print('Received webhook. Request details:')
    
    data = request.get_data()
    try:
        json_data = json.loads(data)
        print('Parsed JSON data:')
        # print(json.dumps(json_data, indent=2))
        
        # Overwrite the latest data in a file
        with open('latest_block.json', 'w') as file:
            json.dump(json_data, file)
    except json.JSONDecodeError as e:
        print('Error parsing JSON:', str(e))
        print('Raw body:', data.decode())
    
    return Response('Webhook received', status=200)

# Helper function to read the latest data
def read_latest_block():
    if os.path.exists('latest_block.json'):
        with open('latest_block.json', 'r') as file:
            return json.load(file)
    return None

if __name__ == '__main__':
    app2.run(debug= True, port=5000)
