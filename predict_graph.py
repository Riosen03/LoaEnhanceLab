import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

DB_PATH = "enhance.db"

# INDEX ↔ TIME
BASE_INDEX    = 17206146
BASE_DATETIME = datetime(2024, 7, 10, 12, 30, 0)
INDEX_STEP    = 3      # index 3 증가당
MINUTES_STEP  = 5      # 5분

# 1주일 = 7일 * 24시간 * 60분 / 5분
STEPS_PER_WEEK   = int((7 * 24 * 60) / MINUTES_STEP)   # = 2016
INDEXES_PER_WEEK = STEPS_PER_WEEK * INDEX_STEP         # = 6048

# ===== 아이템 ID =====
WEAPON_STONE = 1101      # 운명의 파괴석
ARMOR_STONE  = 1201      # 운명의 수호석
BREAK_STONE  = 1011      # 운명의 돌파석
FUSION_STONE = 1021      # 아비도스 융화 재료
FRAGMENT     = 1030      # 운명의 파편
BREATH_FIRE  = 2101      # 용암의 숨결
BREATH_ICE   = 2201      # 빙하의 숨결
GOLD         = 1000      # 골드 ~ 시세X, 개수만 쓰기

BOOK_N_W_11_14 = 3101    # 야금술 : 업화 [11-14]
BOOK_N_W_15_18 = 3102    # 야금술 : 업화 [15-18]
BOOK_N_W_19_20 = 3103    # 야금술 : 업화 [19-20]

BOOK_N_A_11_14 = 3201    # 재봉술 : 업화 [11-14]
BOOK_N_A_15_18 = 3202    # 재봉술 : 업화 [15-18]
BOOK_N_A_19_20 = 3203    # 재봉술 : 업화 [19-20]

BOOK_A_W = {1: 4101, 2: 4102, 3: 4103, 4: 4104}  # 장인의 야금술
BOOK_A_A = {1: 4201, 2: 4202, 3: 4203, 4: 4204}  # 장인의 재봉술


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def index_to_datetime(idx: int) -> datetime:
    delta_index = idx - BASE_INDEX
    minutes = delta_index * (MINUTES_STEP / INDEX_STEP)
    return BASE_DATETIME + timedelta(minutes=minutes)


def datetime_to_index(dt: datetime) -> int:
    delta = dt - BASE_DATETIME
    minutes = delta.total_seconds() / 60
    idx = BASE_INDEX + minutes * (INDEX_STEP / MINUTES_STEP)
    return int(round(idx))

def clean_price_series(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    s = s.mask((s <= 0) | s.isna())
    s = s.interpolate(method="linear", limit_direction="both")
    return s


def plot_item_history_and_forecast(item_id: int):
    conn = get_conn()

    df_hist = pd.read_sql_query(
        """
        SELECT history_index, unit_price
        FROM PriceHistoryData
        WHERE item_id = ?
        ORDER BY history_index ASC
        """,
        conn,
        params=(item_id,)
    )

    df_pred = pd.read_sql_query(
        """
        SELECT predict_index, predict_unit_price
        FROM PricePredictData
        WHERE item_id = ?
        ORDER BY predict_index ASC
        """,
        conn,
        params=(item_id,)
    )

    conn.close()

    if df_hist.empty:
        print(f"[WARN] item_id={item_id}: 과거 데이터 없음")
        return

    # 0/이상값 정리, 보간
    df_hist["unit_price"] = clean_price_series(df_hist["unit_price"])

    # 시간 컬럼
    df_hist["dt"] = df_hist["history_index"].apply(index_to_datetime)

    # 최근 2주로 cut
    last_time = df_hist["dt"].max()
    cutoff = last_time - timedelta(days=14)
    df_hist_recent = df_hist[df_hist["dt"] >= cutoff]

    plt.figure(figsize=(18, 4))
    plt.plot(
        df_hist_recent["dt"],
        df_hist_recent["unit_price"],
        label="history (last 2 weeks)",
    )

    if not df_pred.empty:
        df_pred["dt"] = df_pred["predict_index"].apply(index_to_datetime)
        df_pred_recent = df_pred[df_pred["dt"] >= cutoff]

        plt.plot(
            df_pred_recent["dt"],
            df_pred_recent["predict_unit_price"],
            "--",
            label="forecast(1week)",
        )

    plt.xlabel("time")
    plt.ylabel("unit price")
    plt.title(f"Item {item_id} history + forecast (last 2 weeks)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    print(f"[Success] item_id={item_id}: 최근 2주 + 예측 그래프 출력 완료")

if __name__ == "__main__":
    target_item = int(input("item_id 입력: "))
    plot_item_history_and_forecast(target_item)