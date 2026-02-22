import datetime
import json
import os
import re
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
TRANSLATION_CACHE_FILE = "translation_cache.json"
MAX_RANK_PER_CATEGORY = 30

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


def load_translation_cache():
    if not os.path.exists(TRANSLATION_CACHE_FILE):
        return {}
    try:
        with open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_translation_cache(cache):
    with open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)


def translate_with_deepl(text, target_lang):
    api_key = os.getenv("DEEPL_API_KEY")
    if not api_key or not text:
        return None

    payload = urlencode({
        "auth_key": api_key,
        "text": text,
        "target_lang": target_lang,
        "source_lang": "KO",
    }).encode("utf-8")

    request = Request(
        "https://api-free.deepl.com/v2/translate",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["translations"][0]["text"]
    except Exception:
        return None


def translate_with_google_ai(text, target_lang):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not text:
        return None

    lang_map = {"EN": "English", "JA": "Japanese"}
    language_name = lang_map.get(target_lang, "English")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Translate the following Korean product text into natural {language_name}. "
                            "Return translated text only.\n"
                            f"Text: {text}"
                        )
                    }
                ]
            }
        ]
    }

    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None


def translate_text(text, target_lang):
    return (
        translate_with_deepl(text, target_lang)
        or translate_with_google_ai(text, target_lang)
    )


def build_i18n(text, cache):
    key = text.strip()
    if not key:
        return {"ko": "", "en": "", "ja": ""}

    cached = cache.get(key, {})
    en = cached.get("en")
    ja = cached.get("ja")

    if not en:
        en = translate_text(key, "EN") or key
    if not ja:
        ja = translate_text(key, "JA") or key

    cache[key] = {"en": en, "ja": ja}
    return {"ko": key, "en": en, "ja": ja}


def parse_rankings(config, html, cache, limit=MAX_RANK_PER_CATEGORY):
    blocks = re.findall(config["item_pattern"], html, re.IGNORECASE | re.DOTALL)
    rankings = []

    for block in blocks:
        name = first_match(config["name_pattern"], block)
        if not name:
            continue

        brand = first_match(config["brand_pattern"], block, "Unknown")
        category_i18n = build_i18n(config["category"], cache)
        brand_i18n = build_i18n(brand, cache)
        name_i18n = build_i18n(name, cache)

        rankings.append(
            {
                "rank": len(rankings) + 1,
                "source": config["source"],
                "category": config["category"],
                "category_i18n": category_i18n,
                "brand": brand,
                "brand_i18n": brand_i18n,
                "name": name,
                "name_i18n": name_i18n,
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
    translation_cache = load_translation_cache()

    for config in CATEGORY_CONFIGS:
        print(f"[{config['source']} - {config['category']}] fetching {config['url']}")
        try:
            html = fetch_html(config["url"])
            parsed = parse_rankings(config, html, translation_cache)
            print(f"[{config['source']} - {config['category']}] parsed {len(parsed)}")
            all_rankings.extend(parsed)
        except (HTTPError, URLError, TimeoutError) as error:
            print(f"[{config['source']} - {config['category']}] request failed: {error}")
        except Exception as error:
            print(f"[{config['source']} - {config['category']}] parse failed: {error}")

    save_translation_cache(translation_cache)

    return {
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fx_rate": 1350,
        "translation": {
            "provider": "deepl_or_google_ai(optional)",
            "cache_file": TRANSLATION_CACHE_FILE,
            "languages": ["ko", "en", "ja"],
            "keys": ["DEEPL_API_KEY", "GEMINI_API_KEY"],
        },
        "rankings": all_rankings,
    }


if __name__ == "__main__":
    result = collect_all_rankings()
    with open("data.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    print(f"data.json saved ({len(result['rankings'])} items)")
