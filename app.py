from flask import Flask, render_template, request, jsonify
from chatbot_regular import generate_one_time_response
from chatbot_rag_qa import chatbot_rag_qa_call
import os

app = Flask(__name__)
user_files   = {}
user_storage = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():

    system_message = request.form.get('systemMessage')
    chat_message = request.form.get('chatMessage')
    model = request.form.get('llm_model')
    pdf_file = request.files.get('pdfFile')


    # Safeguard in case no file is uploaded
    if pdf_file:
        pdf_path = os.path.join("uploads", pdf_file.filename)
        pdf_file.save(pdf_path)

    # Function about pdf talk will come here
    #pdf_path

    if pdf_file:
        print(pdf_path)
        chat_bot_response = chatbot_rag_qa_call(file_path=pdf_path
                            ,chosen_model=model
                            ,query=chat_message
                            ,user_id='user_id_1'
                            ,user_files=user_files
                            ,user_storage=user_storage)
        chat_bot_response = chat_bot_response.get('answer', "No answer could be generated.")

    else:
        chat_bot_response = generate_one_time_response(human_message=chat_message,
                                                       system_message=system_message
                                                       ,choosen = model
                                                       ,history=[])

    return jsonify({'response': chat_bot_response})


if __name__ == '__main__':
    # Create upload folder if it does not exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)

