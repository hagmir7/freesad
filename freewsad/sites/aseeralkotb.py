from django.shortcuts import render
from django.http import JsonResponse
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import errorcode
import datetime
import requests
import re
import os
import uuid
import json
from difflib import SequenceMatcher
from urllib.parse import urlparse, unquote
from .config import *
from unidecode import unidecode


# ============================================================
# Config
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


# Shared session so cookies (Laravel session, XSRF-TOKEN, cf_clearance, etc.)
# persist between requests. This is often what makes the difference between
# "works in browser" and "scraper gets blocked".
_session = None


def _get_session():
    """Lazy-init a requests.Session that persists cookies across calls."""
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update(HEADERS)
        _session = s
        # Warm up the session by hitting homepage and solving the challenge
        try:
            resp = s.get(
                "https://www.aseeralkotb.com/ar", timeout=30, allow_redirects=True
            )
            if "AserElKotb=" in resp.text and len(resp.text) < 3000:
                _solve_antibot_cookie(resp.text, s)
                # One more hit to confirm
                s.get(
                    "https://www.aseeralkotb.com/ar", timeout=30, allow_redirects=True
                )
        except Exception as e:
            print(f"Session warm-up failed (continuing anyway): {e}")
    return _session


def _solve_antibot_cookie(body, session):
    """
    aseeralkotb.com serves a tiny JS-obfuscated stub on first hit that sets
    a cookie like 'AserElKotb=<hash>; path=/' and reloads. We parse the
    cookie value out of the obfuscated JS and install it on our session.

    Returns True if a cookie was found and set, False otherwise.
    """
    # The cookie name appears literally in the JS array.
    # Pattern: AserElKotb=<32 hex chars>;\x20path=/;
    m = re.search(r"(AserElKotb=[a-fA-F0-9]+)", body or "")
    if not m:
        return False

    cookie_str = m.group(1)
    try:
        name, value = cookie_str.split("=", 1)
        session.cookies.set(name, value, domain="www.aseeralkotb.com", path="/")
        # Also set on the bare domain just in case
        session.cookies.set(name, value, domain=".aseeralkotb.com", path="/")
        print(f"Anti-bot cookie solved: {name}={value[:12]}...")
        return True
    except Exception as e:
        print(f"Failed to install anti-bot cookie: {e}")
        return False


def _fetch_with_antibot(url, session, max_retries=2):
    """
    Fetch a URL, transparently handling aseeralkotb's JS cookie challenge.
    If the response is the tiny anti-bot stub, extract the cookie and retry.
    """
    resp = session.get(url, timeout=30, allow_redirects=True)

    for attempt in range(max_retries):
        body = resp.text

        # Detect the anti-bot stub: small body + 'AserElKotb=' cookie-setting JS
        is_challenge = (
            len(body) < 3000
            and "AserElKotb=" in body
            and "document" in body
            and "cookie" in body
        )
        if not is_challenge:
            return resp

        print(f"Anti-bot challenge detected on {url} (attempt {attempt + 1})")
        if not _solve_antibot_cookie(body, session):
            # Couldn't parse the cookie; give up and return what we have
            return resp

        # Retry with the cookie now installed
        resp = session.get(url, timeout=30, allow_redirects=True)

    return resp


if os.environ.get("CPANEL") == "1":
    config = {
        "user": "agha6919_books_admin",
        "password": "Guigou.1998@",
        "host": "localhost",
        "database": "agha6919_books",
        "raise_on_warnings": True,
    }
    FILES_FOLDER = "/home/agha6919/books/storage/app/public/book_files/"
    IMAGES_FOLDER = "/home/agha6919/books/storage/app/public/book_images/"
    AUTHOR_IMAGES_FOLDER = "/home/agha6919/books/storage/app/public/author_images/"
    CATEGORY_IMAGES_FOLDER = "/home/agha6919/books/storage/app/public/category_images/"
else:
    config = {
        "user": "root",
        "password": "",
        "host": "localhost",
        "database": "books",
        "raise_on_warnings": True,
    }
    FILES_FOLDER = "D:/Dev/laravel/books/storage/app/public/book_files/"
    IMAGES_FOLDER = "D:/Dev/laravel/books/storage/app/public/book_images/"
    AUTHOR_IMAGES_FOLDER = "D:/Dev/laravel/books/storage/app/public/author_images/"
    CATEGORY_IMAGES_FOLDER = "D:/Dev/laravel/books/storage/app/public/category_images/"

data_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# Small helpers
# ============================================================


def extract_image_url(style):
    if not style:
        return None
    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
    return match.group(1) if match else None


def get_year(text):
    if not text:
        return None
    numbers = re.findall(r"\d+", text)
    return numbers[0] if numbers else None


def generate_slug(text):
    if not text:
        return str(uuid.uuid4())[:10]
    latin_text = unidecode(text)
    slug = re.sub(r"[^\w\s-]", "", latin_text.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-") or str(uuid.uuid4())[:10]


# ============================================================
# Duplicate detection
# ============================================================

STOP_WORDS = {
    "book",
    "books",
    "the",
    "a",
    "an",
    "of",
    "and",
    "in",
    "on",
    "to",
    "for",
    "pdf",
    "edition",
    "ed",
    "vol",
    "volume",
    "part",
    "full",
    "complete",
    "novel",
    "story",
    "stories",
    "series",
    "collection",
    "tales",
    "guide",
    "كتاب",
    "كتب",
    "في",
    "من",
    "الى",
    "على",
    "و",
    "أو",
    "الـ",
    "ال",
    "جزء",
    "الجزء",
    "طبعة",
    "الطبعة",
    "مجلد",
    "المجلد",
    "كامل",
    "كاملة",
    "نسخة",
    "رواية",
    "روايه",
    "الرواية",
    "الروايه",
    "روايات",
    "قصة",
    "قصه",
    "القصة",
    "القصه",
    "قصص",
    "ديوان",
    "الديوان",
    "دواوين",
    "مجموعة",
    "مجموعه",
    "المجموعة",
    "المجموعه",
    "مسرحية",
    "مسرحيه",
    "المسرحية",
    "المسرحيه",
    "سلسلة",
    "سلسله",
    "السلسلة",
    "السلسله",
    "دراسة",
    "دراسه",
    "الدراسة",
    "الدراسه",
    "دراسات",
    "موسوعة",
    "موسوعه",
    "الموسوعة",
    "الموسوعه",
    "معجم",
    "المعجم",
    "قاموس",
    "القاموس",
}


def normalize_name(text):
    if not text:
        return ""
    s = text
    s = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    s = s.lower()
    s = re.sub(r"[^\w\u0600-\u06FF]+", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    tokens = [t for t in s.split(" ") if t and t not in STOP_WORDS]
    return " ".join(tokens)


# Matches subtitle separators: colon, em/en-dash, pipe -- with whitespace around
# (or a colon/full-width colon by itself). Used to split "Main Title : Subtitle"
# so we can compare main-title-to-main-title.
SUBTITLE_SEPARATOR_RE = re.compile(r"\s*[:：\-–—|]\s+")


def main_title_only(text):
    """
    Return the part of a title before any subtitle separator.
    'استرداد عمر : من السيرة...' -> 'استرداد عمر'
    'Rich Dad Poor Dad: The Classic' -> 'Rich Dad Poor Dad'
    """
    if not text:
        return ""
    parts = SUBTITLE_SEPARATOR_RE.split(text, maxsplit=1)
    return parts[0] if parts else text


def similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate_title(new_title, existing_title, threshold=0.85):
    a = normalize_name(new_title)
    b = normalize_name(existing_title)
    if not a or not b:
        return False
    if a == b:
        return True

    # Rule: subtitle-stripping. If either title has ':', '-', '—', '|' followed
    # by a subtitle, compare the main-title parts. Handles:
    #   'استرداد عمر' vs 'استرداد عمر : من السيرة إلى المسيرة'
    #   'Rich Dad Poor Dad' vs 'Rich Dad Poor Dad: The Classic'
    a_main = normalize_name(main_title_only(new_title))
    b_main = normalize_name(main_title_only(existing_title))
    if a_main and b_main:
        if a_main == b_main:
            return True
        if a_main == b or b_main == a:
            return True

    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return False
    shorter, longer = (
        (tokens_a, tokens_b) if len(tokens_a) <= len(tokens_b) else (tokens_b, tokens_a)
    )
    if (
        len(shorter) >= 2
        and shorter.issubset(longer)
        and len(shorter) / len(longer) >= 0.6
    ):
        return True
    if len(shorter) == 1 and shorter.issubset(longer):
        only_token = next(iter(shorter))
        if len(only_token) >= 6:
            return True
    return similarity(a, b) >= threshold


def find_duplicate_book(name):
    if not name:
        return None
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT id, name FROM books")
        for book_id, existing_name in cursor.fetchall():
            if is_duplicate_title(name, existing_name):
                return (book_id, existing_name)
        return None
    except mysql.connector.Error as err:
        print(f"Error checking duplicate book: {err}")
        return None
    finally:
        cursor.close()
        cnx.close()


# ============================================================
# File download
# ============================================================


def download_file(url, folder_path, file_prefix, default_ext=".jpg"):
    if not url:
        return None
    try:
        session = _get_session()
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        parsed_path = urlparse(url).path
        file_extension = os.path.splitext(parsed_path)[1]
        if not file_extension or len(file_extension) > 6:
            file_extension = default_ext
        filename = f"{file_prefix}_{uuid.uuid4().hex[:10]}{file_extension}"
        file_path = os.path.join(folder_path, filename)
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filename
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
        return None


# ============================================================
# Author & Category
# ============================================================


def get_or_create_category(name, image_url=None, description=None):
    if not name:
        name = "Uncategorized"

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT id, name FROM book_categories")
        for cat_id, existing in cursor.fetchall():
            if is_duplicate_title(name, existing):
                return cat_id

        image_filename = None
        if image_url:
            saved = download_file(image_url, CATEGORY_IMAGES_FOLDER, "category_img")
            if saved:
                image_filename = f"category_images/{saved}"

        insert_query = """
            INSERT INTO book_categories
                (name, title, image, description, slug, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_query,
            (
                name,
                name,
                image_filename,
                description,
                generate_slug(name),
                data_now,
                data_now,
            ),
        )
        cnx.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        cnx.close()


def get_or_create_author(full_name, image_url=None, description=None):
    if not full_name:
        full_name = "Unknown Author"

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT id, full_name FROM authors")
        for author_id, existing in cursor.fetchall():
            if is_duplicate_title(full_name, existing):
                return author_id

        image_filename = None
        if image_url:
            saved = download_file(image_url, AUTHOR_IMAGES_FOLDER, "author_img")
            if saved:
                image_filename = f"author_images/{saved}"

        insert_query = """
            INSERT INTO authors
                (full_name, description, image, verified, slug, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_query,
            (
                full_name,
                description,
                image_filename,
                0,
                generate_slug(full_name),
                data_now,
                data_now,
            ),
        )
        cnx.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        cnx.close()


# ============================================================
# Book insertion
# ============================================================


def send_data(data):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        add_book = """
            INSERT INTO books
                (name, title, user_id, author_id, book_category_id, language_id,
                 type, pages, size, image, description, body, tags, file,
                 is_public, slug, site_id, copyright_date, verified, isbn,
                 created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("name"),
            data.get("title"),
            data.get("user_id", 1),
            data.get("author_id"),
            data.get("book_category_id"),
            data.get("language_id", 2),
            data.get("type", "PDF"),
            data.get("pages"),
            data.get("size"),
            data.get("image"),
            data.get("description"),
            data.get("body"),
            data.get("tags"),
            data.get("file"),
            data.get("is_public", 0),
            data.get("slug"),
            data.get("site_id"),
            data.get("copyright_date"),
            data.get("verified", 0),
            data.get("isbn"),
            data.get("created_at"),
            data.get("updated_at"),
        )

        cursor.execute(add_book, values)
        cnx.commit()
        print(f"Saved book: {data.get('name')}")
        return True

    except mysql.connector.Error as err:
        if err.errno == 1062:
            print(f"Duplicate entry detected for book: {data.get('name')}")
            try:
                if data.get("image"):
                    path = os.path.join(
                        IMAGES_FOLDER, data["image"].replace("book_images/", "")
                    )
                    if os.path.exists(path):
                        os.remove(path)
            except OSError as e:
                print(f"Error removing image: {e}")
        else:
            print(f"DB error: {err}")
        return False

    finally:
        if "cursor" in locals():
            cursor.close()
        if "cnx" in locals():
            cnx.close()


# ============================================================
# Scrape a single book page from aseeralkotb.com
# ============================================================


def _safe_text(el):
    return el.get_text(strip=True) if el else None


def _meta_row_value(soup, label):
    """Find a <dd> whose sibling <dt> text matches `label` inside a single-book metadata <dl>."""
    # scope to the single-book metadata block when possible
    scope = soup.select_one("div.single-book__metadata") or soup
    for dt in scope.select("dl dt"):
        if label in dt.get_text(strip=True):
            dd = dt.find_next_sibling("dd")
            if dd:
                return dd
    return None


def _extract_from_jsonld(soup):
    """
    Extract book info from the <script type='application/ld+json'> block.
    This is the most reliable source on aseeralkotb.
    """
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            text = script.string or script.get_text()
            if not text:
                continue
            data = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            continue

        # Some pages wrap in a list
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "Book":
                return item
    return None


def scrape_aseeralkotb_book(book_id):
    """
    Scrape a single book from https://www.aseeralkotb.com/ar/books/{book_id}
    Returns a dict of book info or {'error': ...}.
    """
    url = f"https://www.aseeralkotb.com/ar/books/{book_id}"
    try:
        session = _get_session()
        resp = _fetch_with_antibot(url, session)

        if resp.status_code in (404, 410):
            return {"error": f"Not found ({resp.status_code})"}
        if resp.status_code >= 400:
            return {"error": f"HTTP {resp.status_code}"}

        body = resp.text

        # Soft-404 / anti-bot detection
        if len(body) < 1000:
            return {
                "error": f"Response too short ({len(body)} bytes) - likely anti-bot block"
            }

        # Cloudflare / challenge pages
        lower = body[:5000].lower()
        if (
            "cf-browser-verification" in lower
            or "attention required" in lower
            or "just a moment" in lower
        ):
            return {"error": "Cloudflare challenge page returned"}

        # Redirected to listing/home?
        final_path = urlparse(resp.url).path
        if final_path in ("/ar", "/ar/", "/", "/ar/books", "/ar/books/"):
            return {"error": "Redirected to listing (book doesn't exist)"}

        soup = BeautifulSoup(body, "html.parser")

        # --- 1) Prefer JSON-LD (most reliable) ---
        ld = _extract_from_jsonld(soup) or {}

        # --- 2) Title ---
        # IMPORTANT: the page has many h1[itemprop=name] (main book + similar-book cards).
        # Grab ONLY the one inside <article> or the main book wrapper.
        name = None
        for selector in [
            'div[wire\\:name="books.show"] h1[itemprop="name"]',
            "article h1[itemprop='name']",
            "aside h1[itemprop='name']",
        ]:
            el = soup.select_one(selector)
            if el:
                name = _safe_text(el)
                if name:
                    break

        # Fall back to JSON-LD title
        if not name and ld.get("name"):
            name = ld["name"].strip()

        # Fall back to <title> tag minus site suffix
        if not name:
            title_tag = soup.find("title")
            if title_tag:
                t = title_tag.get_text(strip=True)
                # Remove common suffix like " - عصير الكتب"
                t = re.sub(r"\s*[-–|]\s*عصير\s*الكتب\s*$", "", t)
                name = t or None

        if not name:
            return {"error": "No title found (likely not a book page)"}

        # Reject generic site-level titles
        generic_markers = ["عصير الكتب", "الصفحة الرئيسية", "غير موجود", "404"]
        if any(m in name for m in generic_markers) and len(name) < 40:
            return {"error": f"Looks like a non-book page (title: '{name}')"}

        # --- 3) Cover image ---
        image_url = ld.get("image")
        if not image_url:
            img_el = soup.select_one('picture img[itemprop="contentUrl"]')
            if img_el and img_el.get("src"):
                image_url = img_el["src"]
        if not image_url:
            meta_img = soup.select_one('meta[itemprop="image"]')
            if meta_img and meta_img.get("content"):
                image_url = meta_img["content"]

        # --- 4) Description ---
        description = None
        if ld.get("description"):
            # JSON-LD description may contain HTML entities
            desc_soup = BeautifulSoup(ld["description"], "html.parser")
            description = desc_soup.get_text(" ", strip=True)
        if not description:
            desc_el = soup.select_one('div.description[itemprop="description"]')
            if desc_el:
                description = desc_el.get_text(separator=" ", strip=True)

        # --- 5) Metadata ---
        author_dd = _meta_row_value(soup, "المؤلفون")
        pages_dd = _meta_row_value(soup, "الصفحات")
        year_dd = _meta_row_value(soup, "سنة النشر")
        publisher_dd = _meta_row_value(soup, "دار النشر")
        cat_dd = _meta_row_value(soup, "الأقسام")
        isbn_dd = _meta_row_value(soup, "ISBN")
        cover_type_dd = _meta_row_value(soup, "نوع الغلاف")
        format_dd = _meta_row_value(soup, "الصيغة")

        # Author: JSON-LD first, then DOM
        author_name = None
        if ld.get("author"):
            authors_ld = ld["author"]
            if isinstance(authors_ld, list) and authors_ld:
                author_name = (
                    authors_ld[0].get("name")
                    if isinstance(authors_ld[0], dict)
                    else None
                )
            elif isinstance(authors_ld, dict):
                author_name = authors_ld.get("name")
        if not author_name and author_dd:
            a = author_dd.find("a")
            author_name = _safe_text(a) or _safe_text(author_dd)

        category_name = None
        if cat_dd:
            a = cat_dd.find("a")
            category_name = _safe_text(a) or _safe_text(cat_dd)
        if not category_name and ld.get("genre"):
            g = ld["genre"]
            if isinstance(g, list) and g:
                category_name = g[0]
            elif isinstance(g, str):
                category_name = g

        publisher = None
        if ld.get("publisher") and isinstance(ld["publisher"], dict):
            publisher = ld["publisher"].get("name")
        if not publisher and publisher_dd:
            a = publisher_dd.find("a")
            publisher = _safe_text(a) or _safe_text(publisher_dd)

        pages = get_year(_safe_text(pages_dd)) or (
            str(ld["numberOfPages"]) if ld.get("numberOfPages") else None
        )
        year = get_year(_safe_text(year_dd)) or (
            str(ld["datePublished"])[:4] if ld.get("datePublished") else None
        )
        isbn = ld.get("isbn")
        if not isbn and isbn_dd:
            span = isbn_dd.find("span", {"itemprop": "productID"}) or isbn_dd.find(
                "span"
            )
            isbn = _safe_text(span) or _safe_text(isbn_dd)
        cover_type = _safe_text(cover_type_dd)
        fmt = _safe_text(format_dd)

        # --- 6) Author card (bio + small image) ---
        author_image_url = None
        author_bio = None
        author_section = soup.select_one("section.authors")
        if author_section:
            bio_img = author_section.select_one("h3 img")
            if bio_img:
                author_image_url = bio_img.get("src") or bio_img.get("data-src")
            bio_p = author_section.select_one("p.description")
            if bio_p:
                span = bio_p.find("span")
                author_bio = (
                    span.get_text(separator=" ", strip=True)
                    if span
                    else bio_p.get_text(separator=" ", strip=True)
                )
                author_bio = re.sub(
                    r"\s*(عرض المزيد|عرض الأقل)\s*$", "", author_bio or ""
                ).strip()

        return {
            "source_id": book_id,
            "url": url,
            "name": name,
            "image_url": image_url,
            "description": description,
            "pages": pages,
            "year": year,
            "isbn": isbn,
            "cover_type": cover_type,
            "format": fmt,
            "publisher": publisher,
            "author_name": author_name,
            "author_image_url": author_image_url,
            "author_bio": author_bio,
            "category_name": category_name,
        }

    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        return {"error": f"Parse error: {e}"}


# ============================================================
# Build + save
# ============================================================


def prepare_and_save_book(book_info):
    clean_name = re.sub(r"\s+", " ", book_info["name"]).strip()

    author_id = get_or_create_author(
        full_name=book_info.get("author_name"),
        image_url=book_info.get("author_image_url"),
        description=book_info.get("author_bio"),
    )

    category_id = get_or_create_category(
        name=book_info.get("category_name"),
        image_url=None,
        description=None,
    )

    image_filename = None
    if book_info.get("image_url"):
        saved = download_file(book_info["image_url"], IMAGES_FOLDER, "book_img")
        if saved:
            image_filename = f"book_images/{saved}"

    fmt = (book_info.get("format") or "").strip()
    cover_type = (book_info.get("cover_type") or "").strip()
    btype = "PDF"

    copyright_date = None
    if book_info.get("year"):
        try:
            copyright_date = f"{int(book_info['year'])}-01-01"
        except (ValueError, TypeError):
            copyright_date = None

    pages_val = None
    if book_info.get("pages"):
        try:
            pages_val = int(book_info["pages"])
        except (ValueError, TypeError):
            pages_val = None

    data = {
        "name": clean_name,
        "title": clean_name,
        "user_id": 1,
        "author_id": author_id,
        "book_category_id": category_id,
        "language_id": 2,
        "type": btype,
        "pages": pages_val,
        "size": None,
        "image": image_filename,
        "description": book_info.get("description"),
        "body": book_info.get("description"),
        "tags": (book_info.get("category_name") or "")
        + (f", {cover_type}" if cover_type else ""),
        "file": None,
        "is_public": 0,
        "slug": generate_slug(clean_name),
        "site_id": 6,
        "copyright_date": copyright_date,
        "verified": 0,
        "isbn": book_info.get("isbn"),
        "created_at": data_now,
        "updated_at": data_now,
    }

    return send_data(data)


# ============================================================
# Views
# ============================================================


def index(request):
    return render(request, "index.html", {})


def debug_fetch(request):
    """
    Debug helper: fetch a single book page and return raw diagnostics.
    Usage: /debug-fetch?id=80
    Shows status code, final URL, response size, and first 2000 chars of body
    so you can compare what the server sends the scraper vs what you see in browser.
    """
    book_id = request.GET.get("id", "80")
    url = f"https://www.aseeralkotb.com/ar/books/{book_id}"

    try:
        session = _get_session()
        resp = _fetch_with_antibot(url, session)
        body = resp.text

        # Quick signals
        has_jsonld = '"@type": "Book"' in body or '"@type":"Book"' in body
        has_h1_name = 'itemprop="name"' in body
        has_cloudflare = (
            "Cloudflare" in body or "cf-browser-verification" in body or "__cf_" in body
        )
        has_challenge = "challenge" in body.lower() and "captcha" in body.lower()
        looks_like_spa_shell = len(body) < 5000 and "<title>" in body

        return JsonResponse(
            {
                "url": url,
                "final_url": resp.url,
                "status": resp.status_code,
                "content_type": resp.headers.get("Content-Type"),
                "server": resp.headers.get("Server"),
                "body_length": len(body),
                "signals": {
                    "has_jsonld_Book": has_jsonld,
                    "has_itemprop_name": has_h1_name,
                    "has_cloudflare_markers": has_cloudflare,
                    "has_captcha_challenge": has_challenge,
                    "looks_like_spa_shell": looks_like_spa_shell,
                },
                "response_headers": dict(resp.headers),
                "body_head": body[:2000],
                "body_tail": body[-500:] if len(body) > 500 else "",
            },
            json_dumps_params={"ensure_ascii": False, "indent": 2},
        )
    except Exception as e:
        return JsonResponse({"url": url, "error": str(e)})


def aseeralkotb(request):
    """
    Scrape books from aseeralkotb.com by iterating book IDs.
    Usage: /aseeralkotb?start=10&end=50
    """
    result = []
    saved_count = 0
    error_count = 0
    skipped_count = 0
    not_found_count = 0

    start_id = int(request.GET.get("start") or 1)
    end_id = int(request.GET.get("end") or 10)

    for book_id in range(start_id, end_id + 1):
        url = f"https://www.aseeralkotb.com/ar/books/{book_id}"
        print(f"--- Scraping book id={book_id} | {url} ---")
        try:
            info = scrape_aseeralkotb_book(book_id)

            if "error" in info:
                err_msg = info["error"]
                # Count "not found" separately so you can distinguish from real errors
                if (
                    "Not found" in err_msg
                    or "not a book page" in err_msg
                    or "doesn't exist" in err_msg
                ):
                    not_found_count += 1
                    status = "not_found"
                else:
                    error_count += 1
                    status = "error"
                result.append(
                    {
                        "status": status,
                        "id": book_id,
                        "error": err_msg,
                    }
                )
                continue

            existing = find_duplicate_book(info["name"])
            if existing:
                skipped_count += 1
                print(f"Skipping duplicate: '{info['name']}' == '{existing[1]}'")
                result.append(
                    {
                        "status": "skipped",
                        "id": book_id,
                        "book": info["name"],
                        "matched_existing": existing[1],
                        "reason": "Already exists in database (fuzzy match)",
                    }
                )
                continue

            if prepare_and_save_book(info):
                saved_count += 1
                result.append(
                    {
                        "status": "success",
                        "id": book_id,
                        "book": info["name"],
                        "author": info.get("author_name"),
                    }
                )
            else:
                error_count += 1
                result.append(
                    {
                        "status": "error",
                        "id": book_id,
                        "book": info["name"],
                        "error": "Failed to save to database",
                    }
                )

        except Exception as e:
            error_count += 1
            print(f"Unhandled error on id={book_id}: {e}")
            result.append({"status": "error", "id": book_id, "error": str(e)})

    return JsonResponse(
        {
            "message": (
                f"Scraping completed. "
                f"Saved: {saved_count}, Skipped: {skipped_count}, "
                f"NotFound: {not_found_count}, Errors: {error_count}"
            ),
            "saved_count": saved_count,
            "skipped_count": skipped_count,
            "not_found_count": not_found_count,
            "error_count": error_count,
            "results": result,
        },
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )
