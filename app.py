from flask import Flask, render_template, request, jsonify
from chatbot_regular import chatbot_regular
from chatbot_rag_qa import chatbot_rag_qa_call
from jarvis import jarvis
import os
import shutil
from utils.files import save_files
from database.database import DatabaseChatMessageHistory

app = Flask(__name__)
user_storage = {}

@app.route('/')
def home():
    user_id = request.args.get('id')
    #print(user_id)

    # Check if there is a history for the user
    if user_id:
        #TODO Session management will be handled in the future
        session_id = '222'

        # Initialize the database-backed chat history handler
        chat_history_db = DatabaseChatMessageHistory(user_id=user_id, session_id=session_id)
        # Retrieve the chat history from the database
        chat_history = chat_history_db.get_messages(user_id= user_id,session_id=session_id)
        #print(chat_history)
    else:
        chat_history = []
    #print(user_id)
    #print(chat_history)
    # Pass the chat history to the template
    return render_template('index.html', chat_history=chat_history)

@app.route('/submit', methods=['POST'])
def submit():

    system_message = request.form.get('systemMessage')
    chat_message = request.form.get('chatMessage')
    model = request.form.get('llm_model')
    user_id = request.form.get('userID')
    behaviour = request.form.get('behaviour')

    files = request.files.getlist('fileUpload')

    # Safeguard in case no file is uploaded
    if files:
        save_files(user_id,files)

    chatbot_types = {'chatbot_regular':chatbot_regular
                     ,'chatbot_rag_qa': chatbot_rag_qa_call
                     ,'jarvis':jarvis}

    attributes = ({'human_message'  : chat_message
                  ,'system_message' : system_message
                  ,'chosen_model'   : model
                  ,'user_id'        : user_id
                  ,'user_storage'   : user_storage})

    chat_bot_response = chatbot_types.get(behaviour,chatbot_regular)(**attributes)
    #print(1111,chat_bot_response)

    return jsonify({'response': chat_bot_response})

if __name__ == '__main__':
    # Create upload folder if it does not exist
    # If the 'uploads' folder exists, delete it and its contents
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')
    os.makedirs('uploads')
    app.run(host='192.168.86.78',debug=True,port=5000)
