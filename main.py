# main.py
from mysql_connector import search_by_title, search_by_filters, PAGE_SIZE
from mongo_connector import get_top5_queries
from formatter import print_table
from log_writer import save_log

import logging

# Лёгкое логирование (консоль + файл errors.log)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("errors.log", encoding="utf-8")]
)

def menu():
    print("\n*** Movie Finder ***")
    print("(1) Поиск по названию (keyword)")
    print("(2) Показать TOP-5 запросов (Mongo)")
    print("(3) Поиск по жанру/году")
    print("(0) Выход")

def action_search_by_keyword():
    try:
        keyword = input("Введите слово в названии фильма: ").strip()
        if not keyword:
            print("Пустой запрос. Попробуйте ещё.")
            return

        offset, total = 0, 0
        while True:
            rows = search_by_title(keyword, offset)
            if not rows:
                if offset == 0:
                    print("Ничего не найдено.")
                break

            print_table(rows)
            total += len(rows)
            offset += PAGE_SIZE

            if input("Показать ещё (y/n)? ").strip().lower() != "y":
                break

        # лог в Mongo: позиционные аргументы
        save_log("keyword", {"keyword": keyword}, total)

    except Exception as e:
        print(f"Ой, что-то пошло не так: {e}")
        # лог ошибки в Mongo + стек в файл
        save_log("error", {"where": "action_search_by_keyword", "error": str(e)}, 0)
        logging.exception("Ошибка в action_search_by_keyword")

def action_search_by_filters():
    try:
        print("\n=== Поиск по жанру/году ===")
        keyword = (input("Ключевое слово (ENTER — пропустить): ").strip() or None)

        genres_raw = input("Жанры через запятую (например Action,Comedy) (ENTER — пропустить): ").strip()
        genres = [g.strip() for g in genres_raw.split(",") if g.strip()] if genres_raw else None

        year_from = input("Год с (ENTER — пропустить): ").strip()
        year_to   = input("Год по (ENTER — пропустить): ").strip()
        year_from = int(year_from) if year_from else None
        year_to   = int(year_to)   if year_to   else None

        offset, total = 0, 0
        while True:
            rows = search_by_filters(
                keyword=keyword,
                genres=genres,
                year_from=year_from,
                year_to=year_to,
                offset=offset
            )
            if not rows:
                if offset == 0:
                    print("Ничего не найдено.")
                break

            print_table(rows)
            total += len(rows)
            offset += PAGE_SIZE

            if input("Показать ещё (y/n)? ").strip().lower() != "y":
                break

        # лог в Mongo
        save_log("filters",
                 {"keyword": keyword, "genres": genres, "year_from": year_from, "year_to": year_to},
                 total)

    except Exception as e:
        print(f"Ой, что-то пошло не так: {e}")
        save_log("error", {"where": "action_search_by_filters", "error": str(e)}, 0)
        logging.exception("Ошибка в action_search_by_filters")

def action_show_top5():
    try:
        top = get_top5_queries()
        if not top:
            print("Пока нет статистики.")
            return

        print("\n*** TOP-5 запросов из MongoDB ***")
        for i, item in enumerate(top, start=1):
            print(f"{i}. {item['_id']} — {item['count']} раз")

        # по желанию можно логировать сам факт просмотра статистики
        save_log("show_top5", {}, len(top))

    except Exception as e:
        print(f"Ой, что-то пошло не так: {e}")
        save_log("error", {"where": "action_show_top5", "error": str(e)}, 0)
        logging.exception("Ошибка в action_show_top5")

def main():
    while True:
        menu()
        choice = input("Выберите пункт: ").strip()
        if choice == "1":
            action_search_by_keyword()
        elif choice == "2":
            action_show_top5()
        elif choice == "3":
            action_search_by_filters()
        elif choice == "0":
            print("Пока! 👋")
            break
        else:
            print("Неизвестный пункт. Введите 1, 2, 3 или 0.")

if __name__ == "__main__":
    main()