from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    DB_URL = os.getenv("DB_URL")

config = Config()