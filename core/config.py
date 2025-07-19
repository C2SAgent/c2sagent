from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TimeSERIES_KEY = os.getenv("TimeSERIES_KEY")
    TOS_ACCESS_KEY = os.getenv("TOS_ACCESS_KEY")
    TOS_SECRET_KEY = os.getenv("TOS_SECRET_KEY")

settings = Settings()