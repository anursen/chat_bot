from logger import logger, log_exception
import os
from langchain_openai import ChatOpenAI

# Check for OpenAI API key
if not os.getenv('OPENAI_API_KEY'):
    logger.critical('OPENAI_API_KEY not found.')

# Initialize the model
model = ChatOpenAI(model="gpt-4")
print(model.invoke('jahksdjahsd'))

# Define the function to check
def check():
    try:
        # This will raise an error because `asd` is not defined
        print(asd)
        logger.info('Function successful')
    except Exception as e:
        # Use the custom logging function for exceptions
        log_exception(e)

# Call the check function
check()

# Continue with the rest of your code after logging the error
print("Continuing with the rest of the code...")
