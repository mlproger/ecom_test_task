import os
import re
from dotenv import load_dotenv, find_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", 1))
    DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", 5))
    GROUP_RE = re.compile(r'^\d{3}[А-ЯЁ]$', re.IGNORECASE)  
    DATE_FMT = "%d.%m.%Y"