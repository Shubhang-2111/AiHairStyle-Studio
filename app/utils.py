import os
from fastapi import UploadFile
import shutil

def save_upload_file(uploaded_file: UploadFile, save_dir: str):
    save_path = os.path.join(save_dir, uploaded_file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return save_path
