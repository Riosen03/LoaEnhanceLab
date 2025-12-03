import sqlite3
import math

DB_PATH = "enhance.db"

BASE_INDEX = 17206146
ITEM_ID = 1030                   # 운명의 파편
POUCH_IDS = [1031, 1032, 1033]   # 소/중/대 주머니
INF = math.inf

def get_fragment_unit_price() :
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    
    historys = []

    cur.execute(
        "DELETE FROM PriceHistoryData WHERE item_id = ?",
        (ITEM_ID,)
    )

    # 파우치 3개(1031,1032,1033)의 history 가져오기
    for item_id in POUCH_IDS :
        cur.execute(
            """
            SELECT item_id, history_index, unit_price
            FROM PriceHistoryData
            WHERE item_id = ?
            """,
            (item_id,)
        )
        row = cur.fetchall()
        historys.append(row)
    
    Last_index = historys[0][-1][1]

    frag_min_history = []
    for i in range(0, (Last_index-BASE_INDEX+3)//3) :
        prices = []
        price_s = historys[0][i][2] if historys[0][i][2] > 0 else INF
        price_m = historys[1][i][2] if historys[1][i][2] > 0 else INF
        price_l = historys[2][i][2] if historys[2][i][2] > 0 else INF
        prices.append(price_s)
        prices.append(price_m)
        prices.append(price_l)

        min_price = min(prices)
        if min_price == INF : min_price = 0

        frag_min_history.append([BASE_INDEX+i*3, min_price])
    
    for history_index, unit_price in frag_min_history:
        raw_price = int(unit_price)

        cur.execute(
            """
            INSERT INTO PriceHistoryData (item_id, history_index, raw_price, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            (ITEM_ID, history_index, raw_price, unit_price)
        )
    print(f"[Success] 운명의 파편 - 공백(price <= 0) 포함 {len(frag_min_history)}개 데이터 저장 완료")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    get_fragment_unit_price()