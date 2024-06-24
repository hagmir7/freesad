import mysql.connector
from mysql.connector import errorcode
import requests
from .config import *
from bs4 import BeautifulSoup
import datetime
from django.http import JsonResponse

# Db Config
config = {
    "user": "agha6919_books_admin",
    "password": "Guigou.1998@",
    "host": "localhost",
    "database": "agha6919_books",
    "raise_on_warnings": True,
}

data_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_category(category):

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
            slug, tags, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data_book = (
            data.get("name"),
            data.get("title"),
            data.get("file"),
            data.get("image"),
            data.get("user_id"),
            get_author(data.get("author")),
            get_category(data.get("category")),
            data.get("pages"),
            1,
            data.get("size"),
            data.get("type"),
            data.get("body"),
            data.get("description"),
            data.get("is_public"),
            data.get("slug"),
            data.get("tags"),
            data.get("created_at"),
            data.get("updated_at"),
        )

        cursor.execute(add_book, data_book)
        cnx.commit()

        # Executing a query
        # query = ("SELECT * FROM books")
        # cursor.execute(query)

        # Fetching the results
        # for row in cursor:
        #     print(row)

        # Closing the cursor and connection
        print("DB Connected")
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def page_download(url):

    response = requests.get(url, verify=True, headers=headers)
    if response.status_code == 200:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        image = soup.find("div", {"class": "book-cover"}).find("img")["src"]
        file = soup.find("div", {"class": "book-links"}).find("a")["href"]

        images_folder = "/home/agha6919/books/storage/app/public/book_images/"
        files_folder = "/home/agha6919/books/storage/app/public/book_files/"

        image_name = f"{slug(10).upper()}.png"

        file_name = f"{slug(10).upper()}.pdf"

        download_file(extract_base_url(url) + image, f"{images_folder}{image_name}")
        file_url = download_file(
            extract_base_url(url) + file, f"{files_folder}{file_name}"
        )

        title = soup.find("h1").text
        body = soup.find("div", {"class": "book-description"})
        author = soup.find("a", {"itemprop": "author"}).text
        tags = remove_extra_spaces(soup.find_all("tr")[6].find_all("td")[1].text)
        category = remove_extra_spaces(
            delete_word(
                soup.find_all("tr")[1].find_all("td")[1].find("a").text, "Books"
            )
        )
        pages = int(
            str(soup.find("span", {"itemprop": "numberOfPages"}).text).replace(
                " pages", ""
            )
        )
        name = (
            title.replace(" Free PDF Download", "")
            .replace(" Free Download", "")
            .replace(" PDF Download", "")
        )
        size = format_size(get_file_size(file_url))
        book_slug = generate_slug(name)
        description = str(body.text)[0:165] + "..."

        send_data(
            {
                "name": str(name),
                "title": str(title),
                "file": f"book_files/{str(file_name)}",
                "image": f"book_images/{image_name}",
                "is_public": 1,
                "user_id": 1,
                "author": remove_extra_spaces(str(author)),
                "category": remove_extra_spaces(str(category)),
                "pages": int(pages),
                "language": "en",
                "size": str(size),
                "type": "PDF",
                "body": str(body),
                "description": remove_extra_spaces_and_lines(str(description)),
                "slug": book_slug,
                "tags": str(tags),
                "created_at": data_now,
                "updated_at": data_now,
            }
        )

    else:
        print("Book is not exists")


def pdf(request):
    for i in range(600, 6010):
        url = f"https://yes-pdf.com/book/{i}"
        try:
            print(url)
            page_download(url)
        except:
            print("There is an error in url : " + url)
    return JsonResponse({"message": "Scraped Successfully..."})
