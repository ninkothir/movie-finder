from tabulate import tabulate

def print_table(rows):
    if not rows:
        print("Ничего не найдено.")
        return
    headers = rows[0].keys()
    data = [list(r.values()) for r in rows]
    print(tabulate(data, headers=headers, tablefmt="github"))