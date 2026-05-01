import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgre@localhost/manager_agent")
DATABASE_SYNC_URL = os.getenv("DATABASE_SYNC_URL", "postgresql://postgres:postgre@localhost/manager_agent")
TIMESERIES_DATABASE_URL = os.getenv("TIMESERIES_DATABASE_URL", "postgresql+asyncpg://postgres:postgre@localhost/timeseries")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:your_secure_password@localhost:27017/")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "")

TIMESERIES_KEY = os.getenv("TIMESERIES_KEY")
TOS_ACCESS_KEY = os.getenv("TOS_ACCESS_KEY")
TOS_SECRET_KEY = os.getenv("TOS_SECRET_KEY")
