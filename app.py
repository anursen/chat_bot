from flask import Flask, render_template, request, jsonify
from chatbot_regular import chatbot_regular
from chatbot_rag_qa import chatbot_rag_qa_call
from jarvis import jarvis
import os
import shutil
from utils.files import save_files
from utils.prompt_templates import human_message_rag

app = Flask(__name__)
user_storage = {}

@app.route('/')
def home():
    user_id = request.args.get('userID')  # Assuming you retrieve userID somehow (e.g., query param, session)

    # Check if there is a history for the user
    if user_id in user_storage:
        chat_history = user_storage[user_id].messages  # Assuming `messages` is the structure you are storing
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
    print(1111,chat_bot_response)

    return jsonify({'response': chat_bot_response})

if __name__ == '__main__':
    # Create upload folder if it does not exist
    # If the 'uploads' folder exists, delete it and its contents
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')
    os.makedirs('uploads')
    app.run(host='192.168.86.78',debug=True,port=5000)


{'input': 'Tell me about Abdurrahim?',
 'chat_history': [HumanMessage(content='', additional_kwargs={}, response_metadata={}), AIMessage(content="Dear Abdurrahim,\n\nI've taken note of your application for the Senior Data Scientist position at Amplify. Based on the context provided, I can see that you have a strong background in machine learning, predictive modeling, and data science with over five years of experience.\n\nTo answer your question (which wasn't explicitly stated), if you'd like me to do so, I don't know what specific information or follow-up action is required from Amplify at this point. However, based on the tone and content of your application letter, it seems that you're hoping to initiate a review process or perhaps a discussion about your qualifications for the role.\n\nIs there something specific you'd like me to help with regarding your application?", additional_kwargs={}, response_metadata={})], 'context': [Document(metadata={'page': 0, 'source': 'uploads\\user_id1\\Data_Scientist_with_PharmD.pdf'}, page_content='Dear\nHiring\nManager,\nI\nam\nexcited\nto\napply\nfor\nthe\nSenior\nData\nScientist\nposition\nat\nAmplify.\nWith\nover\nfive\nyears\nof\nexperience\nin\nmachine\nlearning,\npredictive\nmodeling,\nand\ndata\nscience,\nincluding\nhands-on\nexpertise\nwith\nAWS\nSageMaker,\nI\nam\nconfident\nin\nmy\nability\nto\ndevelop\nimpactful\nlead-scoring\nmodels\nand\ndrive\ndata-driven\ndecision-making\nacross\nyour\nteams.\nAt\nWells\nFargo,\nI\nled\ncomplex\npredictive\nmodel\ndevelopment,\nimproving\nanalysis\nefficiency\nby\n50%,\nand\nI\nam\neager\nto\nbring\nmy\ndeep\nunderstanding\nof\nstatistical\nmodeling,\ndata\nengineering,\nand\ncross-functional\ncollaboration\nto\nhelp\nAmplify\nachieve\nits\ngoals.\nThank\nyou\nfor\nconsidering\nmy\napplication.\nSincerely,\nAbdurrahim\nNursen'), Document(metadata={'page': 0, 'source': 'uploads\\user_id1\\Data_Scientist_with_PharmD.pdf'}, page_content='Dear\nHiring\nManager,\nI\nam\nexcited\nto\napply\nfor\nthe\nSenior\nData\nScientist\nposition\nat\nAmplify.\nWith\nover\nfive\nyears\nof\nexperience\nin\nmachine\nlearning,\npredictive\nmodeling,\nand\ndata\nscience,\nincluding\nhands-on\nexpertise\nwith\nAWS\nSageMaker,\nI\nam\nconfident\nin\nmy\nability\nto\ndevelop\nimpactful\nlead-scoring\nmodels\nand\ndrive\ndata-driven\ndecision-making\nacross\nyour\nteams.\nAt\nWells\nFargo,\nI\nled\ncomplex\npredictive\nmodel\ndevelopment,\nimproving\nanalysis\nefficiency\nby\n50%,\nand\nI\nam\neager\nto\nbring\nmy\ndeep\nunderstanding\nof\nstatistical\nmodeling,\ndata\nengineering,\nand\ncross-functional\ncollaboration\nto\nhelp\nAmplify\nachieve\nits\ngoals.\nThank\nyou\nfor\nconsidering\nmy\napplication.\nSincerely,\nAbdurrahim\nNursen')], 'answer': "Abdurrahim Nursen is a candidate applying for the Senior Data Scientist position at Amplify. He has over five years of experience in machine learning, predictive modeling, and data science, with hands-on expertise in AWS SageMaker. In his previous role at Wells Fargo, he led the development of complex predictive models, which improved analysis efficiency by 50%. He emphasizes his deep understanding of statistical modeling, data engineering, and cross-functional collaboration, expressing eagerness to contribute to Amplify's goals."}
