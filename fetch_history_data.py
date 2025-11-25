import sqlite3
import requests
import urllib.parse
import time

base_url = "https://api.loachart.com/line_chart?itemName="
DB_PATH = "enhance.db"
BASE_INDEX = 17206146           # (2024/7/10 12:30)
UPDATE_INDEX = 17496363         # (2025/6/11 10:05)

items = [
    (1101, "운명의 파괴석", 2, 17206146),
    (1201, "운명의 수호석", 2, 17206146),
    (1011, "운명의 돌파석", 1, 17206146),
    (1021, "아비도스 융화 재료", 1, 17206146),
    (1031, "운명의 파편 주머니(소)", 3, 17206890),
    (1032, "운명의 파편 주머니(중)", 4, 17273346),
    (1033, "운명의 파편 주머니(대)", 5, 17376162),
    (2101, "용암의 숨결", 1, 17206890),
    (2201, "빙하의 숨결", 1, 17206890),
#    (1000, "골드", 1, 17206146),

    (3101, "야금술 : 업화 [11-14]", 1, 17273202),
    (3102, "야금술 : 업화 [15-18]", 1, 17466126),
    (3103, "야금술 : 업화 [19-20]", 1, 17569071),
    (3201, "재봉술 : 업화 [11-14]", 1, 17273049),
    (3202, "재봉술 : 업화 [15-18]", 1, 17466126),
    (3203, "재봉술 : 업화 [19-20]", 1, 17569038),

    (4101, "장인의 야금술 : 1단계", 1, 17375868),
    (4102, "장인의 야금술 : 2단계", 1, 17375874),
    (4103, "장인의 야금술 : 3단계", 1, 20000000),
    (4104, "장인의 야금술 : 4단계", 1, 20000000),

    (4201, "장인의 재봉술 : 1단계", 1, 17375859),
    (4202, "장인의 재봉술 : 2단계", 1, 17375874),
    (4203, "장인의 재봉술 : 3단계", 1, 20000000),
    (4204, "장인의 재봉술 : 4단계", 1, 20000000)
]


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
        unit_price = float(price)

        cur.execute(
            """
            INSERT INTO PriceHistoryData (item_id, history_index, raw_price, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            (item[0], history_index, raw_price, unit_price)
        )

    conn.commit()


def collect_all() :
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    cur.execute("DELETE FROM PriceHistoryData;")

    for item in items :
        try:
            history = get_history(item)
        except Exception as e:
            print(f"[Failure] {item[1]} 수집 실패(History 없음) → {e}")
            continue
    
        insert_history(conn, item, history)

        print(f"[Success] {item[1]}: 공백(price < 0) 포함 {len(history)}개 데이터 저장 완료")

        time.sleep(0.3)
    

if __name__ == "__main__":
    collect_all()