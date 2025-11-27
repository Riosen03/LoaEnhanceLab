import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_PATH = "enhance.db"
BASE_INDEX = 17206146
BASE_DATETIME = datetime(2024, 7, 10, 12, 30, 0)
INDEX_PER_5MIN = 3
MINUTES_PER_STEP = 5

PREDICT_RANGE = int((7 * 24 * 60) * INDEX_PER_5MIN / MINUTES_PER_STEP)  # = 6048 <= 1주일

def load_item_id(conn) :
    cur = conn.cursor()
    cur.execute(
        """
        SELECT item_id
        FROM Items
        ORDER BY item_id ASC
        """
    )
    items_id = cur.fetchall()
    return items_id

def load_item_history(conn, item_id):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT history_index, unit_price
        FROM PriceHistoryData
        WHERE item_id = ?
        ORDER BY history_index ASC
        """, 
        (item_id,)
    )
    history = cur.fetchall()
    return history





def predict_data() :
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    items_id = load_item_id(conn)
    for item_id in items_id :
        history = load_item_history(conn, item_id)

    conn.close()

if __name__ == "__main__":
    predict_data()