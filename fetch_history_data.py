import sqlite3
import requests
import urllib.parse
import time

base_url = "https://api.loachart.com/line_chart?itemName="
DB_PATH = "enhance.db"
BASE_INDEX = 17206146           # (2024/7/10 12:30)
UPDATE_INDEX = 17496363         # (2025/6/11 10:05)


def get_history(item) :
    encoded_name = urllib.parse.quote_plus(item[1])
    url = f"{base_url}{encoded_name}"

    response = requests.get(url, timeout=10)  # 10초 안에 응답 없으면 에러
    response.raise_for_status()               # 상태코드 200 아니면 예외 발생
    data = response.json()                    # 파이썬 dict로 파싱

    list = data.get("v", [])

    history = []
    now_index = BASE_INDEX
    if item[3] > now_index :
            while item[3] > now_index :
                history.append((now_index, 0))
                now_index += 3
    for row in list:
        index = int(row[0])
        price = float(row[1])
        if index > now_index :
            while index > now_index :
                history.append((now_index, 0))
                now_index += 3
        now_index += 3
        history.append((index, price))
    

    return history


def insert_history(conn, item, history) :
    cur = conn.cursor()

    for history_index, price in history:
        raw_price = int(price)
        if item[2] == 1 :
            unit_price = float(price)
        elif item[2] == 2 :
            if history_index < UPDATE_INDEX :
                unit_price = float(price)/10
            else :
                unit_price = float(price)/100
        else :
            if item[2] == 3 :
                unit_price = float(price)/1000
            elif item[2] == 4 :
                unit_price = float(price)/2000
            elif item[2] == 5 :
                unit_price = float(price)/3000
            


        cur.execute(
            """
            INSERT INTO PriceHistoryData (item_id, history_index, raw_price, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            (item[0], history_index, raw_price, unit_price)
        )

    conn.commit()


def fetch_history_data() :
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    
    cur.execute("DELETE FROM PriceHistoryData;")
    print("기존 시세 데이터 삭제 완료")

    cur.execute("""
        SELECT item_id, item_name, category_id, item_first_index
        FROM Items
        ORDER BY item_id ASC
    """)
    items = cur.fetchall()

    for item in items :
        if item[0] == 1000 or item[0] == 1030 or item[0] == 4103 or item[0] == 4104 or item[0] == 4203 or item[0] == 4204 :
            continue
        
        try:
            history = get_history(item)
        except Exception as e:

            print(f"[Failure] {item[1]} 수집 실패 → {e}")
            continue
    
        insert_history(conn, item, history)

        print(f"[Success] {item[1]} - 공백(price <= 0) 포함 {len(history)}개 데이터 저장 완료")

        time.sleep(0.3)

    conn.close()
    

if __name__ == "__main__":
    fetch_history_data()