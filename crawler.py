import json
import datetime
import time
from playwright.sync_api import sync_playwright

def get_oliveyoung_rankings():
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=True)
        # 실제 사용자처럼 보이게 설정
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 1000}
        )
        page = context.new_page()

        url = "https://www.oliveyoung.co.kr/store/main/getBestList.do"
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 올리브영 랭킹 페이지 접속 중...")
        
        try:
            page.goto(url, wait_until="domcontentloaded")
            
            # 페이지 하단으로 조금씩 스크롤 (이미지 및 데이터 로딩 유도)
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(2)

            # 상품 정보를 담고 있는 요소를 기다림 (최대 10초)
            page.wait_for_selector('.prd_info', timeout=10000)
            
            # 여러 형태의 선택자를 시도하여 데이터 수집
            items = page.query_selector_all('.prd_info')
            
            if len(items) == 0:
                # 다른 선택자 시도 (사이트 구조 변경 대비)
                items = page.query_selector_all('.common_prd_obj')

            print(f"성공! 총 {len(items)}개의 상품을 찾았습니다.")

            products = []
            for idx, item in enumerate(items[:20], 1):
                # 텍스트 추출 시 예외 처리 강화
                try:
                    brand = item.query_selector('.tx_brand').inner_text().strip() if item.query_selector('.tx_brand') else "Brand Unknown"
                    name = item.query_selector('.tx_name').inner_text().strip() if item.query_selector('.tx_name') else "Name Unknown"
                    price_elem = item.query_selector('.tx_cur > .tx_num')
                    price = price_elem.inner_text().strip() if price_elem else "N/A"
                    
                    products.append({
                        "rank": idx,
                        "brand": brand,
                        "name": name,
                        "price": price,
                        "updated_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    })
                except Exception as e:
                    print(f"{idx}번 상품 정보 추출 중 오류: {e}")
            
            browser.close()
            return products

        except Exception as e:
            print(f"에러 발생: {e}")
            # 에러 발생 시 현재 화면 캡처 (디버깅용)
            page.screenshot(path="debug_error.png")
            browser.close()
            return None

if __name__ == "__main__":
    data = get_oliveyoung_rankings()
    if data and len(data) > 0:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("data.json 저장 성공!")
    else:
        print("최종 결과: 데이터가 비어있습니다. (debug_error.png를 확인해 보세요)")