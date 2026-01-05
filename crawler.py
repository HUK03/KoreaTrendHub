import requests
from bs4 import BeautifulSoup
import json
import datetime
import subprocess

def get_oliveyoung_total_rankings():
    # 사용자님이 주신 전체 랭킹 페이지
    url = "https://www.oliveyoung.co.kr/store/main/getBestList.do"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    try:
        print("올리브영 전체 랭킹 데이터를 가져오는 중...")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"접속 실패 (에러 코드: {response.status_code})")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        # 전체 랭킹 상품 정보 추출
        items = soup.select('.prd_info')
        
        print(f"총 {len(items)}개의 상품을 찾았습니다.")
        
        products = []
        for idx, item in enumerate(items[:20], 1): # 상위 20개
            brand = item.select_one('.tx_brand').text.strip()
            name = item.select_one('.tx_name').text.strip()
            price = item.select_one('.tx_cur > .tx_num').text.strip()
            
            products.append({
                "rank": idx,
                "brand": brand,
                "name": name,
                "price": price,
                "updated_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })
        return products

    except Exception as e:
        print(f"에러 발생: {e}")
        return None

if __name__ == "__main__":
    data = get_oliveyoung_total_rankings()
    if data:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("data.json 파일 저장 완료!")
