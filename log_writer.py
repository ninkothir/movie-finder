import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# грузим .env из папки проекта
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

def _get_collection():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGO_DB", "final_project")]
    return db[os.getenv("MONGO_COLLECTION", "final_project_logs")]

def save_log(search_type: str, params: dict, results_count: int):
    """Сохраняем один лог-запрос."""
    try:
        col = _get_collection()
        col.insert_one({
            "timestamp": datetime.utcnow(),
            "search_type": search_type,   # 'keyword' | потом добавим 'genre_year'
            "params": params,             # напр. {'keyword': 'matrix'}
            "results_count": results_count
        })
    except PyMongoError as e:
        print(f"[Mongo error] {e}")

def get_top_queries(limit: int = 5):
    """Возвращаем топ популярных запросов по частоте."""
    try:
        col = _get_collection()
        pipeline = [
            {"$group": {"_id": {"type": "$search_type", "params": "$params"},
                        "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(col.aggregate(pipeline))
    except PyMongoError as e:
        print(f"[Mongo error] {e}")
        return []