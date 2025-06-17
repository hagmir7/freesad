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
from urllib.parse import urlparse
from .config import *


def extract_image_url(style):
    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
    return match.group(1) if match else None


def get_year(text):
    if not text:
        return None
    numbers = re.findall(r"\d+", text)
    return numbers[0] if numbers else None


def generate_slug(text):
    """Generate a URL-friendly slug from text"""
    if not text:
        return str(uuid.uuid4())[:10]

    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")


def download_file(url, folder_path, file_prefix):
    """Download a file and save it locally"""
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()

        # Generate unique filename
        file_extension = os.path.splitext(urlparse(url).path)[1] or ".pdf"
        filename = f"{file_prefix}_{uuid.uuid4().hex[:10]}{file_extension}"
        file_path = os.path.join(folder_path, filename)

        # Create directory if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Save the file
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
    FILES_FOLDER = "/path/to/your/cpanel/files/"
    IMAGES_FOLDER = "/path/to/your/cpanel/images/"
else:
    config = {
        "user": "root",
        "password": "",
        "host": "localhost",
        "database": "books",
        "raise_on_warnings": True,
    }
    FILES_FOLDER = "D:/Dev/filament/books/storage/app/public/book_files/"
    IMAGES_FOLDER = "D:/Dev/filament/books/storage/app/public/book_images/"

data_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_category(category):
    if not category:
        category = "Uncategorized"

    # Establish database connection
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    try:
        # Check if the category exists
        query = "SELECT * FROM book_categories WHERE name = %s"
        cursor.execute(query, (category,))
        result = cursor.fetchone()

        # If the category does not exist, create it
        if result is None:
            insert_query = """
                INSERT INTO book_categories (name, slug, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """
            insert_data = (category, generate_slug(category), data_now, data_now)
            cursor.execute(insert_query, insert_data)
            cnx.commit()  # Commit the transaction

            # Retrieve the new category record
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

    # Establish database connection
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    try:
        # Check if the author exists
        query = "SELECT * FROM authors WHERE full_name = %s"
        cursor.execute(query, (author,))
        result = cursor.fetchone()

        # If the author does not exist, create it
        if result is None:
            insert_query = """
                INSERT INTO authors (full_name, slug, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """
            insert_data = (author, generate_slug(author), data_now, data_now)
            cursor.execute(insert_query, insert_data)
            cnx.commit()  # Commit the transaction

            # Retrieve the new author record
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
        # Establishing the connection
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
            data.get("user_id", 1),  # Default user_id
            get_author(data.get("author")),
            get_category(data.get("category")),
            data.get("pages"),
            1,  # Default language_id
            data.get("size"),
            data.get("type", "pdf"),
            data.get("body"),
            data.get("description"),
            data.get("is_public", 1),
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
        elif err.errno == 1062:  # MySQL error number for duplicate entry
            print(f"Duplicate entry detected for book: {data.get('name')}")
            # Remove downloaded files if they exist
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


def getBook(url, name, author, image):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        # Safe extraction helpers
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

    # Download image if available
    image_filename = None
    if book_info.get("image"):
        image_filename = download_file(book_info["image"], IMAGES_FOLDER, "book_img")
        if image_filename:
            image_filename = f"book_images/{image_filename}"

    # Download first available book file
    file_filename = None
    if book_info.get("download_links"):
        for link in book_info["download_links"]:
            file_filename = download_file(link, FILES_FOLDER, "book_file")
            if file_filename:
                file_filename = f"book_files/{file_filename}"
                break

    # Calculate file size if file was downloaded
    file_size = None
    if file_filename:
        try:
            file_path = os.path.join(
                FILES_FOLDER, file_filename.replace("book_files/", "")
            )
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
        except Exception as e:
            print(f"Error getting file size: {e}")

    return {
        "name": book_info.get("name", "Unknown Title"),
        "title": book_info.get("name", "Unknown Title"),
        "file": file_filename,
        "image": image_filename,
        "user_id": 1,  # Default user
        "author": book_info.get("author", "Unknown Author"),
        "category": book_info.get("category", "Uncategorized"),
        "pages": int(book_info.get("pages", 0)) if book_info.get("pages") else None,
        "size": file_size,
        "type": "pdf",
        "body": book_info.get("description", ""),
        "description": book_info.get("description", ""),
        "is_public": 1,
        "slug": generate_slug(book_info.get("name", "")),
        "tags": book_info.get("category", ""),
        "created_at": data_now,
        "updated_at": data_now,
        "isbn": None,
    }


def scrap(request):
    """Scrape books and save them to database"""
    result = []
    saved_count = 0
    error_count = 0

    try:
        for page in range(1, 3):  # Scrape first 2 pages
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

                    print(f"Processing book: {name}")

                    # Get detailed book information
                    book_info = getBook(href, name, author, image)

                    if "error" not in book_info:
                        # Prepare data for database
                        book_data = prepare_book_data(book_info)

                        # Save to database
                        if send_data(book_data):
                            saved_count += 1
                            result.append(
                                {
                                    "status": "success",
                                    "book": book_info["name"],
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
            "message": f"Scraping completed. Saved: {saved_count}, Errors: {error_count}",
            "saved_count": saved_count,
            "error_count": error_count,
            "results": result,
        },
        safe=False,
    )
