import os

from package.utilities import get_file_contents

OPENAI_API_KEY = get_file_contents('OPENAI_API_KEY')

def set_environment_openai_api_key():
    "Set up value of OPENAI_API_KEY environment variable."
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
