# mongo_connector.py
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Загружаем .env из папки проекта
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# --- подключение к Mongo ---
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]
_collection = _db[MONGO_COLLECTION]   # ВАЖНО: это объект коллекции, а не строка!

def get_top5_queries():
    """
    Возвращает ТОП-5 самых частых keyword-запросов,
    исходя из логов, которые пишет save_log() в log_writer.py:
      {
        "timestamp": ...,
        "search_type": "keyword",
        "params": {"keyword": "..."},
        "results_count": N
      }
    """
    pipeline = [
        {"$match": {"search_type": "keyword"}},
        {"$group": {"_id": "$params.keyword", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    return list(_collection.aggregate(pipeline))

# Можно оставить для короткой проверки файла отдельно
if __name__ == "__main__":
    print("[DEBUG] DB:", MONGO_DB, "COLLECTION:", MONGO_COLLECTION)
    for i, item in enumerate(get_top5_queries(), 1):
        print(f"{i}. {item['_id']} — {item['count']} раз(а)")