from base64 import b64decode
from typing import Dict

def get_submission(data: Dict):
    """Extract the file contents in a student submission"""
    contents = "\n".join([
            file["contents"]
            for file in data['submitted_answers']['_files']
        ])
    return str(b64decode(contents), "utf-8")
