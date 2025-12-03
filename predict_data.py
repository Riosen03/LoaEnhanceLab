import sqlite3
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 필요없는 경고 제거
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

DB_PATH = "enhance.db"

# INDEX ↔ TIME
BASE_INDEX    = 17206146
BASE_DATETIME = datetime(2024, 7, 10, 12, 30, 0)
INDEX_STEP    = 3      # index 3 증가 당
MINUTES_STEP  = 5      # 5분 증가

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
GOLD         = 1000      # 골드 ~ 시세X, 개수만 사용

BOOK_N_W_11_14 = 3101    # 야금술 : 업화 [11-14]
BOOK_N_W_15_18 = 3102    # 야금술 : 업화 [15-18]
BOOK_N_W_19_20 = 3103    # 야금술 : 업화 [19-20]

BOOK_N_A_11_14 = 3201    # 재봉술 : 업화 [11-14]
BOOK_N_A_15_18 = 3202    # 재봉술 : 업화 [15-18]
BOOK_N_A_19_20 = 3203    # 재봉술 : 업화 [19-20]

BOOK_A_W = {1: 4101, 2: 4102, 3: 4103, 4: 4104}  # 장인의 야금술
BOOK_A_A = {1: 4201, 2: 4202, 3: 4203, 4: 4204}  # 장인의 재봉술

# STL / Holt-Winters용 하루 주기 (5분 단위 1일 = 288개)
DAILY_PERIOD = int(24 * 60 / MINUTES_STEP)  # 288
MAX_DAYS = 30
MAX_POINTS  = 10000

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
    # 숫자 변환 (이상한 값은 NaN)
    s = pd.to_numeric(s, errors="coerce")

    # 0 이하, NaN → 결측치로 처리
    s = s.mask((s <= 0) | s.isna())

    # 선형 보간
    s = s.interpolate(method="linear", limit_direction="both")

    return s

def load_history(conn, item_id: int) -> pd.DataFrame:
    df = pd.read_sql_query(
        """
        SELECT history_index, unit_price
        FROM PriceHistoryData
        WHERE item_id = ?
        ORDER BY history_index ASC
        """,
        conn,
        params=(item_id,)
    )
    return df


def _predict_item_stl_core(df: pd.DataFrame, steps: int = STEPS_PER_WEEK) -> tuple[np.ndarray, np.ndarray]:
    # 1) history_index -> datetime 변환해서 최근 MAX_DAYS만 남기기
    df = df.copy()
    df["dt"] = df["history_index"].apply(index_to_datetime)

    last_time = df["dt"].max()
    cutoff = last_time - timedelta(days=MAX_DAYS)
    df = df[df["dt"] >= cutoff]

    # 2) 포인트가 너무 많으면 최근 MAX_POINTS개만 사용
    if len(df) > MAX_POINTS:
        df = df.tail(MAX_POINTS)

    # 3) 시계열 정제
    series = clean_price_series(df["unit_price"])
    series.index = df["history_index"].values

    # 4) 데이터가 너무 적으면 STL/HW 말고 그냥 평균값 선형
    if len(series) < DAILY_PERIOD * 2:  # 최소 2일 분량은 있어야 패턴 잡힘
        last_index = df["history_index"].iloc[-1]
        future_indexes = last_index + INDEX_STEP * np.arange(1, steps + 1)
        mean_val = float(series.mean())
        future_values = np.full(steps, mean_val, dtype=float)
        return future_indexes, future_values

    # 5) STL 분해 (일 단위 계절성)
    stl = STL(series, period=DAILY_PERIOD, robust=False)  # robust=False로 조금 더 빠르게
    res = stl.fit()

    trend = res.trend
    seasonal = res.seasonal
    combined = trend + seasonal  # 노이즈 제거된 시계열

    # 6) Holt-Winters (추세 + 계절성)
    model = ExponentialSmoothing(
        combined,
        trend="add",
        seasonal="add",
        seasonal_periods=DAILY_PERIOD,
    ).fit(optimized=True)

    future_values = model.forecast(steps)

    # 7) 예측 index 생성 (5분마다 index +3)
    last_index = df["history_index"].iloc[-1]
    future_indexes = last_index + INDEX_STEP * np.arange(1, steps + 1)

    return future_indexes, np.asarray(future_values, dtype=float)

def predict_item(item_id: int, use_last_n: int | None = None):
    conn = get_conn()
    df = load_history(conn, item_id)

    if df.empty:
        print(f"[WARN] item_id={item_id}: history 없음")
        conn.close()
        return

    # 값 부여시 일부만 사용
    if use_last_n is not None and len(df) > use_last_n:
        df = df.tail(use_last_n)

    try:
        future_indexes, preds = _predict_item_stl_core(df, steps=STEPS_PER_WEEK)
    except Exception as e:
        # STL/HW가 실패하면 fallback으로 "최근 평균값 수평선" 사용
        print(f"[WARN] item_id={item_id}: STL/HoltWinter 예측 실패, fallback 사용 ({e})")
        last_index = df["history_index"].iloc[-1]
        future_indexes = last_index + INDEX_STEP * np.arange(1, STEPS_PER_WEEK + 1)
        mean_val = float(clean_price_series(df["unit_price"]).mean())
        preds = np.full(STEPS_PER_WEEK, mean_val, dtype=float)

    # 음수 방지
    preds = np.where(preds < 0, 0, preds)

    cur = conn.cursor()

    # 이 아이템 기존 예측 삭제 후 새로 생성
    cur.execute(
        "DELETE FROM PricePredictData WHERE item_id = ?",
        (item_id,)
    )

    rows = []
    for idx, p in zip(future_indexes, preds):
        unit_price = float(p)
        raw_price = int(round(unit_price))
        rows.append((item_id, int(idx), raw_price, unit_price))

    cur.executemany(
        """
        INSERT INTO PricePredictData
        (item_id, predict_index, predict_raw_price, predict_unit_price)
        VALUES (?, ?, ?, ?)
        """,
        rows
    )

    conn.commit()
    conn.close()
    print(f"[OK] item_id={item_id}: STL-HoltWinter 1주일 예측 {len(rows)}개 저장 완료")


def predict_all_items(use_last_n: int | None = None):
    conn = get_conn()
    item_ids = pd.read_sql_query(
        "SELECT DISTINCT item_id FROM PriceHistoryData ORDER BY item_id",
        conn
    )["item_id"].tolist()
    conn.close()

    for item_id in item_ids:
        predict_item(item_id, use_last_n=use_last_n)


if __name__ == "__main__":
    # predict_item(1101)
    predict_all_items()