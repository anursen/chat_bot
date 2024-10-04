from flask import Flask, render_template, request, jsonify
from chatbot_regular import generate_one_time_response
from chatbot_rag_qa import chatbot_rag_qa_call
import os
import shutil
from utils.files import save_files

app = Flask(__name__)
user_storage = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():

    system_message = request.form.get('systemMessage')
    chat_message = request.form.get('chatMessage')
    model = request.form.get('llm_model')
    user_id = request.form.get('userID')
    #get the list of files
    files = request.files.getlist('fileUpload')

    # Safeguard in case no file is uploaded
    if files:
        save_files(user_id,files)

    #Rag Routine
    if files: # Go and activate the rag routine
        chat_bot_response = chatbot_rag_qa_call(chosen_model=model
                                                ,query=chat_message
                                                ,system_message = system_message
                                                ,user_id=user_id
                                                ,user_storage=user_storage)
        chat_bot_response = chat_bot_response.get('answer', "No answer could be generated.")
    #Regular ChatBot
    else:
        chat_bot_response = generate_one_time_response(human_message=chat_message,
                                                       system_message=system_message
                                                       ,chosen_model = model
                                                       ,user_id = user_id
                                                       ,user_storage = user_storage)

    #print(chat_bot_response)
    return jsonify({'response': chat_bot_response})

if __name__ == '__main__':
    # Create upload folder if it does not exist
    # If the 'uploads' folder exists, delete it and its contents
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')
    os.makedirs('uploads')
    app.run(host='192.168.86.78',debug=True,port=5000)