import init_db
import insert_seed_data
import fetch_history_data
import get_fragment_unit_price
import insert_seed_data_from_excel

if __name__ == "__main__":
    try :
        init_db.init_db()
        insert_seed_data.insert_seed_data()
        fetch_history_data.fetch_history_data()
        get_fragment_unit_price.get_fragment_unit_price()
        insert_seed_data_from_excel.seed_from_excel()
        print("DB 및 기반 데이터 생성 완료")
    except Exception as e :
        print("생성 실패")

    
    
