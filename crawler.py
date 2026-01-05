import json
import datetime
import os
from playwright.sync_api import sync_playwright

def get_oliveyoung_rankings():
    with sync_playwright() as p:
        # 1. 브라우저 설정 강화 (사람처럼 보이게 하기)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100010001"
        
        try:
            print(f"Connecting to {url}...")
            # 타임아웃을 60초로 늘리고, 페이지가 완전히 로드될 때까지 기다림
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2. 보안 팝업이나 쿠키 안내가 있다면 닫기 (선택 사항)
            page.wait_for_timeout(5000) # 페이지 안정화를 위해 5초 대기

            # 3. 디버깅용 스크린샷 찍기 (에러 분석용)
            page.screenshot(path="debug_screen.png")
            print("Screenshot saved as debug_screen.png")

            # 4. 데이터 추출 시도
            # .prd_info가 나타날 때까지 기다리되, 실패해도 에러로 멈추지 않게 함
            items_selector = '.prd_info'
            if page.query_selector(items_selector):
                items = page.query_selector_all(items_selector)
                print(f"Found {len(items)} items.")
                
                products = []
                for idx, item in enumerate(items[:20], 1):
                    brand = item.query_selector('.tx_brand').inner_text().strip()
                    name = item.query_selector('.tx_name').inner_text().strip()
                    price_elem = item.query_selector('.tx_cur > .tx_num')
                    price = price_elem.inner_text().strip() if price_elem else "N/A"
                    
                    products.append({
                        "rank": idx,
                        "brand": brand,
                        "name": name,
                        "price": price,
                        "updated_at": str(datetime.datetime.now())
                    })
                return products
            else:
                print("Element .prd_info not found. Check debug_screen.png")
                return None

        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="error_screen.png")
            return None
        finally:
            browser.close()

if __name__ == "__main__":
    data = get_oliveyoung_rankings()
    if data:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved {len(data)} items.")
    else:
        print("Final check: Data collection failed.")
