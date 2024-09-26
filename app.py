from flask import Flask, render_template, request, jsonify
from chat_bot import generate_one_time_response
import os

app = Flask(__name__)

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