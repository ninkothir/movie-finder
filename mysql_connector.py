# mysql_connector.py
import os
from pathlib import Path
from mysql.connector import connect, Error
from dotenv import load_dotenv

# грузим .env рядом с файлом
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

PAGE_SIZE = 10

def get_mysql_connection():
    """Создаёт подключение к MySQL из .env (host, user, password, database)."""
    host = os.getenv("host")
    user = os.getenv("user")
    password = os.getenv("password")
    database = os.getenv("database")
    return connect(host=host, user=user, password=password, database=database, port=3306)

def search_by_title(keyword: str, offset: int = 0):
    """Поиск по названию с пагинацией."""
    try:
        with get_mysql_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT f.film_id, f.title, f.release_year, f.rating
                    FROM film AS f
                    WHERE f.title LIKE %s
                    ORDER BY f.title
                    LIMIT %s OFFSET %s
                    """,
                    (f"%{keyword}%", PAGE_SIZE, offset)
                )
                return cur.fetchall()
    except Error as e:
        print(f"MySQL error: {e}")
        return []

def search_by_filters(keyword=None, genres=None, year_from=None, year_to=None, offset=0):
    """
    Поиск фильмов с пагинацией (PAGE_SIZE) по фильтрам:
      - keyword: подстрока в названии (регистронезависимо)
      - genres: список жанров (регистронезависимо), напр. ["Action","Comedy"]
      - year_from / year_to: диапазон release_year
    Возвращает: film_id, title, release_year, genres (строка)
    """
    where = []
    params = []

    # keyword: регистронезависимо
    if keyword:
        where.append("LOWER(f.title) LIKE %s")
        params.append(f"%{keyword.lower()}%")

    if year_from is not None:
        where.append("f.release_year >= %s")
        params.append(year_from)

    if year_to is not None:
        where.append("f.release_year <= %s")
        params.append(year_to)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # жанры: регистронезависимо через EXISTS
    genre_exists_sql = ""
    if genres:
        # если других условий нет — добавим WHERE 1=1, чтобы корректно приклеить AND EXISTS
        if not where_sql:
            where_sql = "WHERE 1=1"
        placeholders = ", ".join(["%s"] * len(genres))
        genre_exists_sql = f"""
            AND EXISTS (
                SELECT 1
                FROM film_category fc2
                JOIN category c2 ON c2.category_id = fc2.category_id
                WHERE fc2.film_id = f.film_id
                  AND LOWER(c2.name) IN ({placeholders})
            )
        """
        params.extend([g.lower() for g in genres])

    sql = f"""
        SELECT
            f.film_id,
            f.title,
            f.release_year,
            COALESCE(GROUP_CONCAT(DISTINCT c.name ORDER BY c.name SEPARATOR ', '), '-') AS genres
        FROM film f
        LEFT JOIN film_category fc ON fc.film_id = f.film_id
        LEFT JOIN category c ON c.category_id = fc.category_id
        {where_sql}
        {genre_exists_sql}
        GROUP BY f.film_id, f.title, f.release_year
        ORDER BY f.title
        LIMIT %s OFFSET %s
    """
    params.extend([PAGE_SIZE, offset])

    try:
        with get_mysql_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                return cur.fetchall()
    except Error as e:
        print(f"MySQL error: {e}")
        return []