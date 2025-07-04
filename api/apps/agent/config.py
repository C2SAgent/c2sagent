from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgre@localhost/manager_agent")

settings = Settings()