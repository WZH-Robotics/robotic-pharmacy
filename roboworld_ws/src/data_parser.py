import re

item_dict = {
    '스완슨 비타민': 'vit_s',
    '커클랜드 비타민': 'vit_c',
    '호바흐 비타민': 'vit_h',
    '메가씨 비타민': 'vit_m',

    '민티아 화이트': 'mint_w',
    '민티아 블루': 'mint_b',
    '민티아 포도': 'mint_g',
    '젤리빈': 'jelly'
}

# 시간대 리스트 (순서가 중요: 아침, 점심, 저녁)
time_periods = ['아침', '점심', '저녁']

# 데이터를 파싱하는 함수
def parse_kiosk_data(data):
    # Name과 Contents를 구분 (첫 번째 줄은 필요 없으므로 무시)
    _, contents = data.split('|', 1)

    # 시간대별로 데이터를 구분 (중괄호 {}로 구분된 내용 파싱)
    time_blocks = re.findall(r'\{(.*?)\}', contents)

    # 항목별로 시간대 정보를 담을 딕셔너리
    item_time_dict = {}

    for block in time_blocks:
        # 시간대와 내용을 구분
        time_part, items_part = block.split('|', 1)
        time_part = time_part.strip()  # 시간대 ('아침', '점심', '저녁')
        
        # 항목별로 나누고 딕셔너리 형태로 변환
        for item in items_part.split(','):
            item_name, item_count = item.split(':')
            item_name = item_name.strip()
            item_count = item_count.strip()

            # '3알', '3개' 등에서 숫자만 추출 (정규식 사용)
            quantity = re.search(r'\d+', item_count).group()

            # 사전에서 해당 아이템 변환 (dictionary 변환)
            if item_name in item_dict:
                item_key = item_dict[item_name]

                # 해당 항목의 시간대별 수량을 추적
                if item_key not in item_time_dict:
                    item_time_dict[item_key] = ['0', '0', '0']  # 아침, 점심, 저녁 3자리

                # 시간대에 맞는 인덱스에 수량을 입력 (아침=0, 점심=1, 저녁=2)
                time_index = time_periods.index(time_part)
                item_time_dict[item_key][time_index] = quantity

    # 각 항목을 3자리 숫자로 변환
    converted_data = {key: ''.join(value) for key, value in item_time_dict.items()}
    final_data = str(converted_data).replace('{','').replace('}','').replace("'",'')
    return final_data

# kiosk로부터 받는 데이터 예시
raw_data1 = """Name : 하츄핑|
{아침 | 호바흐 비타민 : 1알, 커클랜드 비타민 : 1알},
{점심 | 젤리빈 : 2알},
{저녁 | 호바흐 비타민 : 1알, 커클랜드 비타민 : 1알}"""

raw_data2 = """Name : 하츄핑|
{아침 | 스완슨 비타민 : 1알, 메가씨 비타민 : 1알},
{점심 | 젤리빈 : 2알, 민티아 칼피스 : 1알},
{저녁 | 스완슨 비타민 : 1알, 메가씨 비타민 : 1알}"""

#parsed_data = parse_kiosk_data(raw_data2)
#print(parsed_data)
#encoded_data = str(parsed_data).encode()