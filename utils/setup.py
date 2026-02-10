import os
import dotenv
dotenv.load_dotenv()

# Prefer explicit REDIS_URL, then local/remote variants
REDIS_URL = os.getenv("REDIS_URL")

broker_url = f"{REDIS_URL}/0" if REDIS_URL else None
result_backend = f"{REDIS_URL}/1" if REDIS_URL else None
