import os
valid_extensions = {'.pdf', '.csv'}  # Set of valid file extensions
from utils.logger import logger
from werkzeug.utils import secure_filename

def save_files(user_id, files):
    for file in files:
        if not file.filename.lower().endswith(tuple(valid_extensions)):
            return {"response": f"Invalid file format: {file.filename}. Only PDF and CSV files are allowed."}, 400

        user_folder = os.path.join("uploads", user_id)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        file_path = os.path.join(user_folder, secure_filename(file.filename))
        file.save(file_path)
        logger.critical(f"{file} saved{file_path}")
        #print('file saved')
