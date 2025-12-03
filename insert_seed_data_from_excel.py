import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "enhance.db"
EXCEL_PATH = "로아 강화 재료 소모량 시트.xlsx"
BASE_INDEX = 17206146
BASE_DATETIME = datetime(2024, 7, 10, 12, 30, 0)

# ===== 아이템 ID =====
WEAPON_STONE = 1101      # 운명의 파괴석
ARMOR_STONE  = 1201      # 운명의 수호석
BREAK_STONE  = 1011      # 운명의 돌파석
FUSION_STONE = 1021      # 아비도스 융화 재료
FRAGMENT     = 1030      # 운명의 파편
BREATH_FIRE  = 2101      # 용암의 숨결 (무기)
BREATH_ICE   = 2201      # 빙하의 숨결 (방어구)
GOLD         = 1000      # 골드 ~ 시세X

BOOK_N_W_11_14 = 3101    # 야금술 : 업화 [11-14]
BOOK_N_W_15_18 = 3102    # 야금술 : 업화 [15-18]
BOOK_N_W_19_20 = 3103    # 야금술 : 업화 [19-20]

BOOK_N_A_11_14 = 3201    # 재봉술 : 업화 [11-14]
BOOK_N_A_15_18 = 3202    # 재봉술 : 업화 [15-18]
BOOK_N_A_19_20 = 3203    # 재봉술 : 업화 [19-20]

BOOK_A_W = {1: 4101, 2: 4102, 3: 4103, 4: 4104}  # 장인의 야금술
BOOK_A_A = {1: 4201, 2: 4202, 3: 4203, 4: 4204}  # 장인의 재봉술


def get_N_W_book_id(level) :
    if 11 <= level <= 14:
        return BOOK_N_W_11_14
    if 15 <= level <= 18:
        return BOOK_N_W_15_18
    if 19 <= level <= 20:
        return BOOK_N_W_19_20
    return None

def get_N_A_book_id(level):
    if 11 <= level <= 14:
        return BOOK_N_A_11_14
    if 15 <= level <= 18:
        return BOOK_N_A_15_18
    if 19 <= level <= 20:
        return BOOK_N_A_19_20
    return None


def seed_from_excel() :
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    xls = pd.ExcelFile(EXCEL_PATH)

    # 일반 재련(N) - 무기(W)
    df = pd.read_excel(xls, sheet_name="일반재련(무기)")

    for _, row in df.iterrows() :
        type_id = 1
        level = int(row["시도단계"])
        breath = int(row["숨결"])
        breath_avail = 1 if breath > 0 else 0
        book = str(row["책(t/f)"]).strip().lower()
        if 11 <= level <= 14:
            require_book_id = BOOK_N_W_11_14
        elif 15 <= level <= 18:
            require_book_id = BOOK_N_W_15_18
        elif 19 <= level <= 20:
            require_book_id = BOOK_N_W_19_20
        else : require_book_id = None
        
        book_avail = 1 if (require_book_id is not None and book == "t") else 0
        base_success_rate = float(row["기본확률"])

        cur.execute(
            "SELECT stage_id FROM EnhanceStage WHERE type_id = ? AND level = ?",
            (type_id, level)
        )
        row_t = cur.fetchone()

        if row_t:
            stage_id = row_t[0]
            cur.execute(
                """
                UPDATE EnhanceStage
                SET base_success_rate = ?, breath_avail = ?, book_avail = ?, require_book_id = ?
                WHERE stage_id = ?
                """,
                (base_success_rate, breath_avail, book_avail, require_book_id, stage_id)
            )
        else:
            cur.execute(
                """
                INSERT INTO EnhanceStage
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
            )
            stage_id = cur.lastrowid

        cur.execute("DELETE FROM EnhanceCost WHERE stage_id = ?", (stage_id,))

        costs = [
            (WEAPON_STONE,row["파괴석"]),
            (BREAK_STONE, row["돌파석"]),
            (FUSION_STONE,row["융화재료"]),
            (FRAGMENT,    row["파편"]),
            (GOLD,        row["골드"]),
            (BREATH_FIRE, breath)
        ]

        for item_id, item_quantity in costs :
            item_quantity = int(item_quantity)
            cur.execute(
                "INSERT INTO EnhanceCost (stage_id, item_id, item_quantity) VALUES (?, ?, ?)", 
                (stage_id, item_id, item_quantity)
            )

    # 일반 재련 - 방어구
    df = pd.read_excel(xls, sheet_name="일반재련(방어구)")

    for _, row in df.iterrows() :
        type_id = 2
        level = int(row["시도단계"])
        breath = int(row["숨결"])
        breath_avail = 1 if breath > 0 else 0
        book = str(row["책(t/f)"]).strip().lower()
        require_book_id = get_N_A_book_id(level)
        book_avail = 1 if (require_book_id is not None and book == "t") else 0
        base_success_rate = float(row["기본확률"])

        cur.execute(
            "SELECT stage_id FROM EnhanceStage WHERE type_id = ? AND level = ?",
            (type_id, level)
        )
        row_t = cur.fetchone()

        if row_t:
            stage_id = row_t[0]
            cur.execute(
                """
                UPDATE EnhanceStage
                SET base_success_rate = ?, breath_avail = ?, book_avail = ?, require_book_id = ?
                WHERE stage_id = ?
                """,
                (base_success_rate, breath_avail, book_avail, require_book_id, stage_id)
            )
        else:
            cur.execute(
                """
                INSERT INTO EnhanceStage
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
            )
            stage_id = cur.lastrowid

        cur.execute("DELETE FROM EnhanceCost WHERE stage_id = ?", (stage_id,))

        costs = [
            (ARMOR_STONE, row["수호석"]),
            (BREAK_STONE, row["돌파석"]),
            (FUSION_STONE,row["융화재료"]),
            (FRAGMENT,    row["파편"]),
            (GOLD,        row["골드"]),
            (BREATH_ICE,  breath)
        ]

        for item_id, item_quantity in costs :
            item_quantity = int(item_quantity)
            cur.execute(
                "INSERT INTO EnhanceCost (stage_id, item_id, item_quantity) VALUES (?, ?, ?)", 
                (stage_id, item_id, item_quantity)
            )

    # 상급 재련 - 무기
    df = pd.read_excel(xls, sheet_name="상급재련(무기)")

    for _, row in df.iterrows() :
        type_id = 3
        level = int(row["담금질단계"])
        breath = int(row["숨결"])
        breath_avail = 1 if breath > 0 else 0
        book = str(row["책"]).strip().lower()
        require_book_id = BOOK_A_W.get(level)
        book_avail = 1 if (require_book_id is not None and book == "t") else 0
        base_success_rate = float(100)

        cur.execute(
            "SELECT stage_id FROM EnhanceStage WHERE type_id = ? AND level = ?",
            (type_id, level)
        )
        row_t = cur.fetchone()

        if row_t:
            stage_id = row_t[0]
            cur.execute(
                """
                UPDATE EnhanceStage
                SET base_success_rate = ?, breath_avail = ?, book_avail = ?, require_book_id = ?
                WHERE stage_id = ?
                """,
                (base_success_rate, breath_avail, book_avail, require_book_id, stage_id)
            )
        else:
            cur.execute(
                """
                INSERT INTO EnhanceStage
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
            )
            stage_id = cur.lastrowid

        cur.execute("DELETE FROM EnhanceCost WHERE stage_id = ?", (stage_id,))

        costs = [
            (WEAPON_STONE,row["파괴석"]),
            (BREAK_STONE, row["돌파석"]),
            (FUSION_STONE,row["융화재료"]),
            (FRAGMENT,    row["파편"]),
            (GOLD,        row["골드"]),
            (BREATH_FIRE, breath)
        ]

        for item_id, item_quantity in costs :
            item_quantity = int(item_quantity)
            cur.execute(
                "INSERT INTO EnhanceCost (stage_id, item_id, item_quantity) VALUES (?, ?, ?)", 
                (stage_id, item_id, item_quantity)
            )

    # 상급 재련 - 방어구
    df = pd.read_excel(xls, sheet_name="상급재련(방어구)")

    for _, row in df.iterrows() :
        type_id = 4
        level = int(row["담금질단계"])
        breath = int(row["숨결"])
        breath_avail = 1 if breath > 0 else 0
        book = str(row["책"]).strip().lower()
        require_book_id = BOOK_A_A.get(level)
        book_avail = 1 if (require_book_id is not None and book == "t") else 0
        base_success_rate = float(100)

        cur.execute(
            "SELECT stage_id FROM EnhanceStage WHERE type_id = ? AND level = ?",
            (type_id, level)
        )
        row_t = cur.fetchone()

        if row_t:
            stage_id = row_t[0]
            cur.execute(
                """
                UPDATE EnhanceStage
                SET base_success_rate = ?, breath_avail = ?, book_avail = ?, require_book_id = ?
                WHERE stage_id = ?
                """,
                (base_success_rate, breath_avail, book_avail, require_book_id, stage_id)
            )
        else:
            cur.execute(
                """
                INSERT INTO EnhanceStage
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (type_id, level, base_success_rate, breath_avail, book_avail, require_book_id)
            )
            stage_id = cur.lastrowid

        cur.execute("DELETE FROM EnhanceCost WHERE stage_id = ?", (stage_id,))

        costs = [
            (ARMOR_STONE, row["수호석"]),
            (BREAK_STONE, row["돌파석"]),
            (FUSION_STONE,row["융화재료"]),
            (FRAGMENT,    row["파편"]),
            (GOLD,        row["골드"]),
            (BREATH_ICE,  breath)
        ]

        for item_id, item_quantity in costs :
            item_quantity = int(item_quantity)
            cur.execute(
                "INSERT INTO EnhanceCost (stage_id, item_id, item_quantity) VALUES (?, ?, ?)", 
                (stage_id, item_id, item_quantity)
            )


    conn.commit()
    conn.close()

    print("엑셀 데이터 로드 및 강화데이터 저장 완료(enhancestage/cost)")

if __name__ == "__main__":
    seed_from_excel()