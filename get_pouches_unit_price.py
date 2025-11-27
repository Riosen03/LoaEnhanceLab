import sqlite3
import math

DB_PATH = "enhance.db"

ITEM_ID = 1030                   # 운명의 파편
POUCH_IDS = [1031, 1032, 1033]   # 소/중/대 주머니
INF = math.inf

def get_pouches_unit_price() :
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    
    historys = []

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
    
    



if __name__ == "__main__":
    get_pouches_unit_price()