import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
KEY_ID=os.getenv('KEY_ID')
KEY_SECRET=os.getenv('KEY_SECRET')
PATH_KODO=os.getenv('PATH_KODO')