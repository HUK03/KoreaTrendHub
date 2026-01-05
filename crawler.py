import requests
from bs4 import BeautifulSoup
import json
import datetime

def get_oliveyoung_rankings():
    # 올리브영 베스트 페이지 (스킨케어 랭킹)
    url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100010001"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    # 제품 목록 추출 (사이트 구조에 따라 선택자는 변경될 수 있습니다)
    items = soup.select('.prd_info')[:20] # 상위 20개만 수집
    
    for idx, item in enumerate(items, 1):
        name = item.select_one('.tx_name').text.strip()
        brand = item.select_one('.tx_brand').text.strip()
        price = item.select_one('.tx_cur > .tx_num').text.strip()
        
        products.append({
            "rank": idx,
            "brand": brand,
            "name": name,
            "price": price,
            "updated_at": str(datetime.datetime.now())
        })
    
    return products

if __name__ == "__main__":
    data = get_oliveyoung_rankings()
    
    # 결과를 JSON 파일로 저장
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("Data collection completed successfully!")
