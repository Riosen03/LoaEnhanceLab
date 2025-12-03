import sqlite3

DB_PATH = "enhance.db"

def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.executescript(
        """
        -- 아이템 카테고리
        CREATE TABLE IF NOT EXISTS ItemCategory (
            category_id   INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL
        );

        -- 아이템 기본 정보
        CREATE TABLE IF NOT EXISTS Items (
            item_id          INTEGER PRIMARY KEY, -- increment 아님 (게임 내 ID 그대로 사용 가정)
            item_name        TEXT NOT NULL,
            category_id      INTEGER NOT NULL,
            item_first_index INTEGER,
            FOREIGN KEY (category_id) REFERENCES ItemCategory(category_id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        );

        -- 과거 시세 데이터
        CREATE TABLE IF NOT EXISTS PriceHistoryData (
            history_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id      INTEGER NOT NULL,
            history_index INTEGER NOT NULL,
            raw_price    INTEGER NOT NULL,
            unit_price   REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(item_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );

        -- 강화 타입 (일반/상급, 무기/방어구 등)
        CREATE TABLE IF NOT EXISTS EnhanceType (
            type_id   INTEGER PRIMARY KEY,
            type_name TEXT NOT NULL
        );

        -- 강화 단계별 기본 정보
        CREATE TABLE IF NOT EXISTS EnhanceStage (
            stage_id          INTEGER PRIMARY KEY,
            type_id           INTEGER NOT NULL,
            level             INTEGER NOT NULL,
            base_success_rate REAL NOT NULL,
            breath_avail      INTEGER NOT NULL DEFAULT 0, -- bool: 0/1
            book_avail        INTEGER NOT NULL DEFAULT 0, -- bool: 0/1
            require_book_id   INTEGER,
            FOREIGN KEY (type_id)         REFERENCES EnhanceType(type_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            FOREIGN KEY (require_book_id) REFERENCES Items(item_id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
        );

        -- 강화 비용 (단계별 소모 재료)
        CREATE TABLE IF NOT EXISTS EnhanceCost (
            cost_id       INTEGER PRIMARY KEY,
            stage_id      INTEGER NOT NULL,
            item_id       INTEGER NOT NULL,
            item_quantity INTEGER NOT NULL,
            FOREIGN KEY (stage_id) REFERENCES EnhanceStage(stage_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE,
            FOREIGN KEY (item_id)  REFERENCES Items(item_id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        );

        -- 시세 예측 결과 저장용
        CREATE TABLE IF NOT EXISTS PricePredictData (
            predict_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id           INTEGER NOT NULL,
            predict_index     INTEGER NOT NULL,
            predict_raw_price INTEGER NOT NULL,
            predict_unit_price REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(item_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );

        -- 인덱스
        CREATE INDEX IF NOT EXISTS idx_price_item ON PriceHistoryData(item_id);
        CREATE INDEX IF NOT EXISTS idx_price_index ON PriceHistoryData(history_index);
        """
    )

    conn.commit()
    conn.close()

    print("DB 및 Entity 생성 완료")


if __name__ == "__main__":
    init_db()