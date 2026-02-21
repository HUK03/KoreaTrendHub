import datetime
import json
import re
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

CATEGORY_CONFIGS = [
    {
        "source": "Olive Young",
        "category": "스킨케어",
        "url": "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=10000010001",
        "item_pattern": r'<li[^>]*class="[^"]*(?:prd|flag)[^"]*"[^>]*>(.*?)</li>',
        "brand_pattern": r'class="tx_brand"[^>]*>(.*?)<',
        "name_pattern": r'class="tx_name"[^>]*>(.*?)<',
        "price_pattern": r'class="tx_num"[^>]*>([\d,]+)<',
        "image_pattern": r'<img[^>]+(?:data-original|src)="([^"]+)"',
    },
    {
        "source": "Olive Young",
        "category": "메이크업",
        "url": "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=10000010002",
        "item_pattern": r'<li[^>]*class="[^"]*(?:prd|flag)[^"]*"[^>]*>(.*?)</li>',
        "brand_pattern": r'class="tx_brand"[^>]*>(.*?)<',
        "name_pattern": r'class="tx_name"[^>]*>(.*?)<',
        "price_pattern": r'class="tx_num"[^>]*>([\d,]+)<',
        "image_pattern": r'<img[^>]+(?:data-original|src)="([^"]+)"',
    },
    {
        "source": "Olive Young",
        "category": "헬스/푸드",
        "url": "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=10000010003",
        "item_pattern": r'<li[^>]*class="[^"]*(?:prd|flag)[^"]*"[^>]*>(.*?)</li>',
        "brand_pattern": r'class="tx_brand"[^>]*>(.*?)<',
        "name_pattern": r'class="tx_name"[^>]*>(.*?)<',
        "price_pattern": r'class="tx_num"[^>]*>([\d,]+)<',
        "image_pattern": r'<img[^>]+(?:data-original|src)="([^"]+)"',
    },
    {
        "source": "Daiso",
        "category": "리빙",
        "url": "https://www.daisomall.co.kr/ds/rank/C105",
        "item_pattern": r'<li[^>]*>(.*?)</li>',
        "brand_pattern": r'class="item-brand"[^>]*>(.*?)<',
        "name_pattern": r'class="item-name"[^>]*>(.*?)<',
        "price_pattern": r'class="(?:num|price)[^\"]*"[^>]*>([\d,]+)<',
        "image_pattern": r'<img[^>]+src="([^"]+)"',
    },
    {
        "source": "Daiso",
        "category": "뷰티",
        "url": "https://www.daisomall.co.kr/ds/rank/C103",
        "item_pattern": r'<li[^>]*>(.*?)</li>',
        "brand_pattern": r'class="item-brand"[^>]*>(.*?)<',
        "name_pattern": r'class="item-name"[^>]*>(.*?)<',
        "price_pattern": r'class="(?:num|price)[^\"]*"[^>]*>([\d,]+)<',
        "image_pattern": r'<img[^>]+src="([^"]+)"',
    },
    {
        "source": "Daiso",
        "category": "주방/식기",
        "url": "https://www.daisomall.co.kr/ds/rank/C101",
        "item_pattern": r'<li[^>]*>(.*?)</li>',
        "brand_pattern": r'class="item-brand"[^>]*>(.*?)<',
        "name_pattern": r'class="item-name"[^>]*>(.*?)<',
        "price_pattern": r'class="(?:num|price)[^\"]*"[^>]*>([\d,]+)<',
        "image_pattern": r'<img[^>]+src="([^"]+)"',
    },
]


def fetch_html(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def clean_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", value))).strip()


def first_match(pattern, text, default=""):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return clean_text(match.group(1)) if match else default


def parse_rankings(config, html, limit=20):
    blocks = re.findall(config["item_pattern"], html, re.IGNORECASE | re.DOTALL)
    rankings = []

    for block in blocks:
        name = first_match(config["name_pattern"], block)
        if not name:
            continue

        rankings.append(
            {
                "rank": len(rankings) + 1,
                "source": config["source"],
                "category": config["category"],
                "brand": first_match(config["brand_pattern"], block, "Unknown"),
                "name": name,
                "price": first_match(config["price_pattern"], block, ""),
                "image_url": first_match(config["image_pattern"], block, ""),
                "link": config["url"],
            }
        )

        if len(rankings) >= limit:
            break

    return rankings


def collect_all_rankings():
    all_rankings = []

    for config in CATEGORY_CONFIGS:
        print(f"[{config['source']} - {config['category']}] fetching {config['url']}")
        try:
            html = fetch_html(config["url"])
            parsed = parse_rankings(config, html)
            print(f"[{config['source']} - {config['category']}] parsed {len(parsed)}")
            all_rankings.extend(parsed)
        except (HTTPError, URLError, TimeoutError) as error:
            print(f"[{config['source']} - {config['category']}] request failed: {error}")
        except Exception as error:
            print(f"[{config['source']} - {config['category']}] parse failed: {error}")

    return {
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fx_rate": 1350,
        "rankings": all_rankings,
    }


if __name__ == "__main__":
    result = collect_all_rankings()
    with open("data.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    print(f"data.json saved ({len(result['rankings'])} items)")
