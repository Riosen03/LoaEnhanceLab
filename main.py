from predict_data import predict_item, predict_all_items
from predict_graph import plot_item_history_and_forecast
from predict_mincost import find_min_cost_for_stage

items = [
        (1101, "운명의 파괴석"),
        (1201, "운명의 수호석"),
        (1011, "운명의 돌파석"),
        (1021, "아비도스 융화 재료"),
        (1030, "운명의 파편"),
        (1031, "운명의 파편 주머니(소)"),
        (1032, "운명의 파편 주머니(중)"),
        (1033, "운명의 파편 주머니(대)"),
        (2101, "용암의 숨결"),
        (2201, "빙하의 숨결"),

        (3101, "야금술 : 업화 [11-14]"),
        (3102, "야금술 : 업화 [15-18]"),
        (3103, "야금술 : 업화 [19-20]"),
        (3201, "재봉술 : 업화 [11-14]"),
        (3202, "재봉술 : 업화 [15-18]"),
        (3203, "재봉술 : 업화 [19-20]"),

        (4101, "장인의 야금술 : 1단계"),
        (4102, "장인의 야금술 : 2단계"),
        (4103, "장인의 야금술 : 3단계"),
        (4104, "장인의 야금술 : 4단계"),

        (4201, "장인의 재봉술 : 1단계"),
        (4202, "장인의 재봉술 : 2단계"),
        (4203, "장인의 재봉술 : 3단계"),
        (4204, "장인의 재봉술 : 4단계")
    ]

def main():
    while True:
        print("\n=== 로아 강화 예측 툴 ===")
        print("1) 특정 재료 1주일 예측 생성 (PricePredictData 저장)")
        print("2) 모든 재료 1주일 예측 생성")
        print("3) 특정 재료의 과거+미래 시세 그래프 보기")
        print("4) 특정 강화 단계의 1회 비용 최소 예상값 + 시각 찾기")
        print("0) 종료")
        sel = input("번호 선택: ").strip()

        if sel == "1":
            for item_id, item_name in items :
                print (item_id, "-", item_name)
            item_id = int(input("item_id 입력: "))
            predict_item(item_id)

        elif sel == "2":
            predict_all_items()

        elif sel == "3":
            for item_id, item_name in items :
                print (item_id, "-", item_name)
            item_id = int(input("item_id 입력: "))
            plot_item_history_and_forecast(item_id)

        elif sel == "4":
            print("type_id: 1=일반무기, 2=일반방어구, 3=상급무기, 4=상급방어구")
            type_id = int(input("type_id 입력: "))
            level = int(input("level(일반:11~25 / 상급:1~4) 입력: "))
            find_min_cost_for_stage(type_id, level)

        elif sel == "0":
            print("종료합니다.")
            break

        else:
            print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()