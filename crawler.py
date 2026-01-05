import json
import datetime
from playwright.sync_api import sync_playwright

def get_oliveyoung_rankings():
    with sync_playwright() as p:
        # 브라우저 실행 (headless=True는 화면을 띄우지 않음을 의미)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 한국 올리브영 스킨케어 랭킹 페이지
        url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100010001"
        
        print(f"Connecting to {url}...")
        page.goto(url, wait_until="networkidle")

        products = []
        
        # 상품 리스트가 나타날 때까지 대기
        page.wait_for_selector('.prd_info')
        items = page.query_selector_all('.prd_info')
        
        print(f"Found {len(items)} items.")

        for idx, item in enumerate(items[:20], 1):
            try:
                # 한국어 정보 그대로 수집
                brand = item.query_selector('.tx_brand').inner_text().strip()
                name = item.query_selector('.tx_name').inner_text().strip()
                # 가격 정보 (할인 전/후가 있을 수 있어 예외처리)
                price_elem = item.query_selector('.tx_cur > .tx_num')
                price = price_elem.inner_text().strip() if price_elem else "N/A"
                
                products.append({
                    "rank": idx,
                    "brand": brand,
                    "name": name,
                    "price": price,
                    "updated_at": str(datetime.datetime.now())
                })
            except Exception as e:
                print(f"Error parsing item {idx}: {e}")

        browser.close()
        return products

if __name__ == "__main__":
    data = get_oliveyoung_rankings()
    
    if data:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved {len(data)} items to data.json")
    else:
        print("Failed to collect data.")
