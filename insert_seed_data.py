import sqlite3

DB_PATH = "enhance.db"

# 아이템 카테고리 기본 정보 입력
def seed_item_category(db_path="enhance.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # (category_id, category_name)
    categories = [
        (1, "single"),
        (2, "stone"),
        (3, "pouch_S"),
        (4, "pouch_M"),
        (5, "pouch_L"),
    ]

    for category_id, name in categories:
        # UPDATE 시도
        cur.execute(
            "UPDATE ItemCategory SET category_name = ? WHERE category_id = ?",
            (name, category_id),
        )
        # 없으면 INSERT
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO ItemCategory (category_id, category_name) VALUES (?, ?)",
                (category_id, name),
            )

    conn.commit()
    conn.close()

# 아이템 정보 입력
def seed_items():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # (item_id, item_name, category_id, item_first_index) // 17206146 -> 2024/07/10 12:30, index +3 -> +5 min
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
        (1000, "골드", 1, 17206146),

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

    for item_id, name, category_id, first_index in items:

        # UPDATE 먼저 시도
        cur.execute(
            "UPDATE Items SET item_name = ?, category_id = ?, item_first_index = ? WHERE item_id = ?",
            (name, category_id, first_index, item_id)
        )

        # UPDATE가 0줄이면 (기존에 없음) INSERT
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO Items (item_id, item_name, category_id, item_first_index) VALUES (?, ?, ?, ?)",
                (item_id, name, category_id, first_index)
            )

    conn.commit()
    conn.close()

# 강화 타입 정보 입력
def seed_enhance_type(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # (type_id, type_name)
    types = [
        (1, "normal_weapon"),     # 일반 재련 (무기)
        (2, "normal_armor"),      # 일반 재련 (방어구)
        (3, "advanced_weapon"),   # 상급 재련 (무기)
        (4, "advanced_armor"),    # 상급 재련 (방어구)
    ]

    for type_id, type_name in types:
        # UPDATE 시도
        cur.execute(
            "UPDATE EnhanceType SET type_name = ? WHERE type_id = ?",
            (type_name, type_id)
        )

        # 없으면 INSERT
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO EnhanceType (type_id, type_name) VALUES (?, ?)",
                (type_id, type_name)
            )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_item_category()
    seed_items()
    seed_enhance_type()
