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
from difflib import SequenceMatcher
from urllib.parse import urlparse
from .config import *
from unidecode import unidecode


def extract_image_url(style):
    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
    return match.group(1) if match else None


def get_year(text):
    if not text:
        return None
    numbers = re.findall(r"\d+", text)
    return numbers[0] if numbers else None


def generate_slug(text):
    """Generate a URL-friendly slug from Arabic or English text."""
    if not text:
        return str(uuid.uuid4())[:10]

    latin_text = unidecode(text)
    slug = re.sub(r"[^\w\s-]", "", latin_text.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")


# ---------- Duplicate-detection helpers ----------

# Common filler/category words (Arabic + English) that shouldn't count when comparing titles.
STOP_WORDS = {
    # English
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
    # Arabic - articles, prepositions, conjunctions
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
    # Arabic - category/genre words commonly prefixing titles
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
    """
    Aggressive normalization for comparison only (not for storage):
    - remove Arabic diacritics/tatweel
    - unify Arabic letter variants
    - lowercase
    - strip punctuation
    - collapse whitespace
    - remove stop words (book, كتاب, pdf, etc.)
    """
    if not text:
        return ""

    s = text

    # Remove Arabic tashkeel (diacritics) and tatweel
    s = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", s)

    # Normalize Arabic letter variants
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")

    # Lowercase latin chars
    s = s.lower()

    # Replace any non-alphanumeric/non-arabic char with space
    s = re.sub(r"[^\w\u0600-\u06FF]+", " ", s, flags=re.UNICODE)

    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()

    # Remove stop words
    tokens = [t for t in s.split(" ") if t and t not in STOP_WORDS]

    return " ".join(tokens)


def similarity(a, b):
    """Return similarity ratio between two strings (0.0 - 1.0)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate_title(new_title, existing_title, threshold=0.85):
    """
    Decide whether two titles refer to the same book.
    Works symmetrically: order of arguments doesn't matter.

    Rules (checked in order):
      1. Exact match after normalization -> duplicate
      2. Full-containment: all tokens of the shorter title appear in the longer,
         AND shorter covers >=60% of longer  (handles 'Rich Dad Poor Dad' vs
         'Rich Dad Poor Dad book')
      3. Single distinctive token: shorter has exactly 1 token, it's contained
         in the longer, AND the token is >=6 characters long  (handles
         'السيلماريلين' vs 'رواية السيلماريلين' when stopwords don't cover
         the prefix word)
      4. SequenceMatcher similarity >= threshold (final fuzzy check)
    """
    a = normalize_name(new_title)
    b = normalize_name(existing_title)

    if not a or not b:
        return False

    if a == b:
        return True

    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return False

    shorter, longer = (
        (tokens_a, tokens_b) if len(tokens_a) <= len(tokens_b) else (tokens_b, tokens_a)
    )

    # Rule 2: full containment with enough coverage
    if (
        len(shorter) >= 2
        and shorter.issubset(longer)
        and len(shorter) / len(longer) >= 0.6
    ):
        return True

    # Rule 3: single distinctive token contained in the other.
    # A long unique word (e.g. 'السيلماريلين', 'Silmarillion') contained in
    # the longer title is a strong duplicate signal on its own. The 6-char
    # minimum prevents short words like 'love', 'dune', '1984' from triggering.
    if len(shorter) == 1 and shorter.issubset(longer):
        only_token = next(iter(shorter))
        if len(only_token) >= 6:
            return True

    # Rule 4: final fuzzy similarity
    return similarity(a, b) >= threshold


def find_duplicate_book(name):
    """
    Scan all existing book names in the DB and return the first one that
    matches `name` according to is_duplicate_title(). Returns (id, name) or None.
    """
    if not name:
        return None

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT id, name FROM books")
        rows = cursor.fetchall()
        for book_id, existing_name in rows:
            if is_duplicate_title(name, existing_name):
                return (book_id, existing_name)
        return None
    except mysql.connector.Error as err:
        print(f"Error checking duplicate book: {err}")
        return None
    finally:
        cursor.close()
        cnx.close()


# -------------------------------------------------


def download_file(url, folder_path, file_prefix):
    """Download a file and save it locally"""
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()

        file_extension = os.path.splitext(urlparse(url).path)[1] or ".pdf"
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


def index(request):
    context = {}
    return render(request, "index.html", context)


HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


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

data_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_category(category):
    if not category:
        category = "Uncategorized"

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    try:
        query = "SELECT * FROM book_categories WHERE name = %s"
        cursor.execute(query, (category,))
        result = cursor.fetchone()

        if result is None:
            insert_query = """
                INSERT INTO book_categories (name, slug, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """
            insert_data = (category, generate_slug(category), data_now, data_now)
            cursor.execute(insert_query, insert_data)
            cnx.commit()

            cursor.execute(query, (category,))
            new_result = cursor.fetchone()
            return new_result[0]
        else:
            return result[0]
    finally:
        cursor.close()
        cnx.close()


def get_author(author):
    if not author:
        author = "Unknown Author"

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    try:
        query = "SELECT * FROM authors WHERE full_name = %s"
        cursor.execute(query, (author,))
        result = cursor.fetchone()

        if result is None:
            insert_query = """
                INSERT INTO authors (full_name, slug, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """
            insert_data = (author, generate_slug(author), data_now, data_now)
            cursor.execute(insert_query, insert_data)
            cnx.commit()

            cursor.execute(query, (author,))
            new_result = cursor.fetchone()
            return new_result[0]
        else:
            return result[0]
    finally:
        cursor.close()
        cnx.close()


def send_data(data):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        add_book = """
            INSERT INTO books
            (name, title, file, image, user_id, author_id, book_category_id,
            pages, language_id, size, type, body, description, is_public,
            slug, tags, created_at, updated_at, isbn)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data_book = (
            data.get("name"),
            data.get("title"),
            data.get("file"),
            data.get("image"),
            data.get("user_id", 1),
            get_author(data.get("author")),
            get_category(data.get("category")),
            data.get("pages"),
            2,
            data.get("size"),
            data.get("type", "pdf"),
            data.get("body"),
            data.get("description"),
            0,
            data.get("slug"),
            data.get("tags"),
            data.get("created_at"),
            data.get("updated_at"),
            data.get("isbn"),
        )

        cursor.execute(add_book, data_book)
        cnx.commit()

        print(f"Successfully saved book: {data.get('name')}")
        return True

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        elif err.errno == 1062:
            print(f"Duplicate entry detected for book: {data.get('name')}")
            try:
                if data.get("file"):
                    file_path = os.path.join(
                        FILES_FOLDER, data.get("file").replace("book_files/", "")
                    )
                    if os.path.exists(file_path):
                        os.remove(file_path)

                if data.get("image"):
                    image_path = os.path.join(
                        IMAGES_FOLDER, data.get("image").replace("book_images/", "")
                    )
                    if os.path.exists(image_path):
                        os.remove(image_path)

            except OSError as e:
                print(f"Error removing files: {e}")
        else:
            print(f"Unhandled database error: {err}")

        return False

    finally:
        if "cursor" in locals():
            cursor.close()
        if "cnx" in locals():
            cnx.close()


def size_format(size):
    if size is None:
        return None

    if isinstance(size, str):
        return size

    try:
        size = float(size)
    except (ValueError, TypeError):
        return None

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{round(size, 2)} {units[unit_index]}"


def getBook(url, name, author, image):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        def safe_text(selector):
            el = soup.select_one(selector)
            return el.text.strip() if el else None

        date = get_year(safe_text("div.book-publication-date"))
        pages = get_year(safe_text("div.book-pages"))
        category = safe_text("div.book-cat a")
        description = safe_text("#description")

        files_div = soup.find("div", class_="book-links")
        if files_div:
            files = files_div.find_all("a")
            links = [link.get("href") for link in files if link.get("href")]
        else:
            links = []

        return {
            "name": name,
            "author": author,
            "image": image,
            "date": date,
            "pages": pages,
            "category": category,
            "description": description,
            "download_links": links,
        }

    except Exception as e:
        print(f"Error scraping book {name}: {e}")
        return {"error": str(e)}


def prepare_book_data(book_info):
    """Prepare book data for database insertion"""

    # Clean display name: strip + collapse whitespace only (keep original language/casing)
    raw_name = book_info.get("name", "Unknown Title") or "Unknown Title"
    clean_name = re.sub(r"\s+", " ", raw_name).strip() or "Unknown Title"

    image_filename = None
    if book_info.get("image"):
        image_filename = download_file(book_info["image"], IMAGES_FOLDER, "book_img")
        if image_filename:
            image_filename = f"book_images/{image_filename}"

    file_filename = None
    if book_info.get("download_links"):
        for link in book_info["download_links"]:
            file_filename = download_file(link, FILES_FOLDER, "book_file")
            if file_filename:
                file_filename = f"book_files/{file_filename}"
                break

    file_size = None
    if file_filename:
        try:
            file_path = os.path.join(
                FILES_FOLDER, file_filename.replace("book_files/", "")
            )
            if os.path.exists(file_path):
                file_size = size_format(os.path.getsize(file_path))
        except Exception as e:
            print(f"Error getting file size: {e}")

    return {
        "name": clean_name,
        "title": clean_name,
        "file": file_filename,
        "image": image_filename,
        "user_id": 1,
        "author": book_info.get("author", "Unknown Author"),
        "category": book_info.get("category", "Uncategorized"),
        "pages": int(book_info.get("pages", 0)) if book_info.get("pages") else None,
        "size": file_size,
        "type": "PDF",
        "body": book_info.get("description", ""),
        "description": book_info.get("description", ""),
        "is_public": 0,
        "slug": generate_slug(clean_name),
        "tags": book_info.get("category", ""),
        "created_at": data_now,
        "updated_at": data_now,
        "isbn": None,
        "language_id": 2,
        "verified": 0,
    }


def scrap(request):
    """Scrape books and save them to database"""
    result = []
    saved_count = 0
    error_count = 0
    skipped_count = 0

    start_page = int(request.GET.get("start") or 1)
    end_page = int(request.GET.get("end") or 3)

    # Track titles saved in THIS run (prevents duplicates within the same scrape session)
    session_titles = []

    try:
        for page in range(start_page, end_page):
            print(f"Scraping page {page}...")
            url = f"https://mktbtypdf.com/library/page/{page}/"
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, "html.parser")
            books = soup.find_all("div", class_="library-book")

            for book in books:
                try:
                    href = book.find("a")["href"]
                    name = book.find("div", class_="book-title").text.strip()
                    author = book.find("div", class_="book-author").text.strip()
                    image = extract_image_url(
                        book.find("div", class_="book-img")["style"]
                    )

                    # --- Fuzzy duplicate check against the DB ---
                    existing = find_duplicate_book(name)
                    if existing:
                        skipped_count += 1
                        print(
                            f"Skipping duplicate: '{name}'  ==  '{existing[1]}' "
                            f"(existing id={existing[0]})"
                        )
                        result.append(
                            {
                                "status": "skipped",
                                "book": name,
                                "matched_existing": existing[1],
                                "reason": "Already exists in database (fuzzy match)",
                            }
                        )
                        continue

                    # --- Also check against titles saved earlier in this same run ---
                    dup_in_session = next(
                        (t for t in session_titles if is_duplicate_title(name, t)),
                        None,
                    )
                    if dup_in_session:
                        skipped_count += 1
                        print(
                            f"Skipping duplicate in same run: '{name}'  ==  '{dup_in_session}'"
                        )
                        result.append(
                            {
                                "status": "skipped",
                                "book": name,
                                "matched_existing": dup_in_session,
                                "reason": "Already scraped in this run",
                            }
                        )
                        continue
                    # -------------------------------------------

                    book_info = getBook(href, name, author, image)

                    if "error" not in book_info:
                        book_data = prepare_book_data(book_info)

                        if send_data(book_data):
                            saved_count += 1
                            session_titles.append(book_data["name"])
                            result.append(
                                {
                                    "status": "success",
                                    "book": book_data["name"],
                                    "author": book_info["author"],
                                }
                            )
                        else:
                            error_count += 1
                            result.append(
                                {
                                    "status": "error",
                                    "book": book_info["name"],
                                    "error": "Failed to save to database",
                                }
                            )
                    else:
                        error_count += 1
                        result.append(
                            {
                                "status": "error",
                                "book": name,
                                "error": book_info["error"],
                            }
                        )

                except Exception as e:
                    error_count += 1
                    print(f"Error processing book: {e}")
                    result.append({"status": "error", "error": str(e)})

    except Exception as e:
        print(f"Error during scraping: {e}")
        return JsonResponse({"error": str(e), "results": result}, safe=False)

    return JsonResponse(
        {
            "message": (
                f"Scraping completed. Saved: {saved_count}, "
                f"Skipped: {skipped_count}, Errors: {error_count}"
            ),
            "saved_count": saved_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "results": result,
        },
        safe=False,
    )
