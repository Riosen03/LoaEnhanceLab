import sqlite3
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

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
BREATH_FIRE  = 2101      # 용암의 숨결 (무기)
BREATH_ICE   = 2201      # 빙하의 숨결 (방어구)
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

def get_stage_id(conn, type_id: int, level: int):
    cur = conn.cursor()
    cur.execute(
        "SELECT stage_id FROM EnhanceStage WHERE type_id = ? AND level = ?",
        (type_id, level)
    )
    row = cur.fetchone()
    return row[0] if row else None


def load_stage_cost_items(conn, stage_id: int):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT item_id, item_quantity
        FROM EnhanceCost
        WHERE stage_id = ?
        """,
        (stage_id,)
    )
    return cur.fetchall()  # [(item_id, qty), ...]


def load_predicted_series(conn, item_id: int) -> pd.DataFrame:
    df = pd.read_sql_query(
        """
        SELECT predict_index, predict_unit_price
        FROM PricePredictData
        WHERE item_id = ?
        ORDER BY predict_index ASC
        """,
        conn,
        params=(item_id,)
    )
    return df


def compute_stage_cost_timeseries(conn, stage_id: int) -> pd.DataFrame | None:
    """
    각 predict_index마다 '강화 1회 비용'을 계산한 시계열 DF를 리턴.
    columns: ["predict_index", "total_cost"]
    """
    cost_items = load_stage_cost_items(conn, stage_id)
    if not cost_items:
        print(f"[WARN] stage_id={stage_id} : EnhanceCost 없음")
        return None

    pred_dfs = []
    gold_qty = 0

    # 예측 시리즈
    for item_id, qty in cost_items:
        if item_id == GOLD:
            gold_qty += qty
            continue

        df_pred = load_predicted_series(conn, item_id)
        if df_pred.empty:
            print(f"[WARN] item_id={item_id} : PricePredictData 없음")
            return None

        df_pred = df_pred.copy()
        df_pred["item_id"] = item_id
        df_pred["quantity"] = qty
        pred_dfs.append(df_pred)

    if not pred_dfs:
        print("[WARN] 예측 대상 재료 없음")
        return None

    # 공통 predict_index 구간 만들기 (inner join)
    base_df = pred_dfs[0][["predict_index", "predict_unit_price"]].rename(
        columns={"predict_unit_price": f"price_{pred_dfs[0]['item_id'].iloc[0]}"}
    )

    for df in pred_dfs[1:]:
        item_id = df["item_id"].iloc[0]
        tmp = df[["predict_index", "predict_unit_price"]].rename(
            columns={"predict_unit_price": f"price_{item_id}"}
        )
        base_df = base_df.merge(tmp, on="predict_index", how="inner")

    if base_df.empty:
        print("[WARN] 공통 예측 index 구간이 없음")
        return None

    # 총 비용 계산
    total_cost = np.zeros(len(base_df), dtype=float)

    for item_id, qty in cost_items:
        if item_id == GOLD:
            total_cost += qty * 1  # 골드는 unit 1로 취급
        else:
            col_name = f"price_{item_id}"
            total_cost += qty * base_df[col_name].values

    result = pd.DataFrame({
        "predict_index": base_df["predict_index"],
        "total_cost": total_cost,
    })
    return result


def find_min_cost_for_stage(type_id: int, level: int):
    conn = get_conn()
    stage_id = get_stage_id(conn, type_id, level)
    if stage_id is None:
        print(f"[ERROR] type_id={type_id}, level={level}: stage 없음")
        conn.close()
        return

    df_cost = compute_stage_cost_timeseries(conn, stage_id)
    conn.close()

    if df_cost is None or df_cost.empty:
        return

    idx_min = df_cost["total_cost"].idxmin()
    best_row = df_cost.loc[idx_min]
    best_index = int(best_row["predict_index"])
    best_cost = float(best_row["total_cost"])
    best_time = index_to_datetime(best_index)

    print(f"[RESULT] type_id={type_id}, level={level}")
    print(f"  ▶ 최소 예상 1회 비용: {best_cost:,.1f} 골드")
    print(f"  ▶ 그 시점 index: {best_index}")
    print(f"  ▶ 예상 시각: {best_time}")

    return best_index, best_time, best_cost, df_cost