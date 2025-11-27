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


