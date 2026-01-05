import json
import datetime
import os
from playwright.sync_api import sync_playwright

def get_oliveyoung_rankings():
    with sync_playwright() as p:
        # 1. 모바일(iPhone 13) 환경 에뮬레이션
        device = p.devices['iPhone 13']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            **device,
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        page = context.new_page()

        # 모바일 베스트 페이지 주소
        url = "https://m.oliveyoung.co.kr/m/main/getBestList.do?dispCatNo=900000100010001"
        
        try:
            print(f"Connecting to Mobile Version: {url}...")
            # 페이지 접속 및 대기
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000) # 자바스크립트 실행 대기

            # 디버깅용 스크린샷 (모바일 화면 확인용)
            page.screenshot(path="debug_screen.png")

            # 모바일 페이지의 제품명 선택자는 다를 수 있습니다. (.common_prd_obj 또는 .prd_name)
            # 여러 후보군 중 하나라도 있으면 가져오도록 설정
            products = []
            items = page.query_selector_all('.common_prd_obj') or page.query_selector_all('.prd_info')
            
            if not items:
                print("Still can't find items. The IP might be blocked.")
                return None

            print(f"Found {len(items)} items on Mobile Site.")

            for idx, item in enumerate(items[:20], 1):
                # 모바일 구조에 맞춘 선택자 (브랜드명/제품명/가격)
                brand = item.query_selector('.brand').inner_text().strip() if item.query_selector('.brand') else "Unknown"
                name = item.query_selector('.prd_name').inner_text().strip() if item.query_selector('.prd_name') else "Unknown"
                price = item.query_selector('.price').inner_text().split('원')[0].strip() if item.query_selector('.price') else "N/A"
                
                products.append({
                    "rank": idx,
                    "brand": brand,
                    "name": name,
                    "price": price,
                    "updated_at": str(datetime.datetime.now())
                })
            return products

        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            browser.close()

if __name__ == "__main__":
    data = get_oliveyoung_rankings()
    if data:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Success! Saved {len(data)} items.")
    else:
        print("Failed. Check debug_screen.png in Actions artifacts.")
