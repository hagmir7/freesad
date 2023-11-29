from base64 import encode
from bs4 import BeautifulSoup, Comment
import requests
from freewsad.models import Post, Language, PostCategory, Book, BookCategory
from django.http import JsonResponse
from .robo import bot
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
import random
import string
import time
from django.contrib.auth.models import User


def slug(length=8):
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}


def download_image(url, id):
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        response.raise_for_status()

        file_temp = NamedTemporaryFile()
        file_temp.write(response.content)
        file_temp.flush()

        post = Book.objects.get(id=id)
        with open(file_temp.name, "rb") as file:
            post.image.save("image.png", File(file))
        print("File saved successfully.")
    else:
        print("Failed to download the file.")


def download_file(url, id):
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        response.raise_for_status()

        file_temp = NamedTemporaryFile()
        file_temp.write(response.content)
        file_temp.flush()

        post = Book.objects.get(id=id)
        with open(file_temp.name, "rb") as file:
            post.file.save("file.pdf", File(file))
        print("File saved successfully.")
    else:
        print("Failed to download the file.")


def page_download(url, data, error):
    if not error:
        page = requests.get(url, verify=True, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        download_btn = soup.find("a", {"class": "download"})["href"]
        url = f"https://www.kotobati.com{download_btn}"
        response = requests.get(url, verify=True, headers=headers)
        if response.status_code == 200:
            response.raise_for_status()

            file_temp = NamedTemporaryFile()
            file_temp.write(response.content)
            file_temp.flush()

            language = data.get("language")
            if language == "English":
                lang = "en"
                title = f"Download {str(data.get('name'))} free PDF"
            else:
                lang = "ar"
                title = f"تحميل  {str(data.get('name'))} PDF مجانا"
            caty = data.get("category")
            if BookCategory.objects.filter(name__icontains=caty).exists():
                category = BookCategory.objects.filter(name__icontains=caty)[0]
            else:
                category = BookCategory.objects.create(
                    name=caty, language=Language.objects.get(code=lang)
                )

            if not Book.objects.filter(name__icontains=data.get("name")):
                book = Book.objects.create(
                    name=str(data.get("name")),
                    title=title,
                    user=User.objects.get(id=1),
                    author=str(data.get("author")),
                    language=Language.objects.get(code=lang),
                    description=str(data.get("body")),
                    tags="رواية, كتاب, قصة, ديوان, تحميل, pdf, download, شعر, مجلد,",
                    category=category,
                    is_public=True
                    # file= ("file.png", File(file)),
                )
                # print(data.get("name"))
                # print(data.get("author"))
                # print(data.get("body"))
                # print(data.get("author"))
                download_image(data.get("image"), book.id)
                download_file(url, book.id)
                time.sleep(5)


def getItem(url):
    print(url)
    page = requests.get(url, verify=True, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    try:
        image = soup.find("div", {"class": "image"}).find("img")
        if image and "data-src" in image.attrs:
            image_url = image["data-src"]
        else:
            image_url = image["src"]
        image = f"https://www.kotobati.com{image_url}"
    except:
        image = "https://vitaldigital.us/wp-content/uploads/2017/11/book-placeholder-small-125x150.png"

    try:
        name = soup.find("h2", {"class": "img-title"}).text
    except Exception as e:
        print(f"Name error: {e}\n")
        name = "Default name"

    try:
        author = soup.find_all("p", {"class": "book-p-info"})[0].text
    except Exception as e:
        print(f"Author error: {e}\n")
        author = "Agmir Hassane"

    try:
        category = soup.find_all("p", {"class": "book-p-info"})[1].text
    except Exception as e:
        category = "التنمية البشرية"
        print(f"Category error: {e}\n")

    language = (
        soup.find("ul", class_="book-table-info")
        .find_all("li")[1]
        .find_all("p")[1]
        .text.strip()
    )
    body = soup.find("div", {"class": "tab-content"})

    try:
        if body:
            body.find("a").decompose()
    except Exception as e:
        print(f"Custom error: {e}")

    data = {
        "image": image,
        "name": name,
        "category": category,
        "author": author,
        "language": language,
        "body": body,
    }

    try:
        download_path = soup.find("a", {"class": "download"})["href"]
        path = f"https://www.kotobati.com{download_path}"
        page_download(path, data, False)
    except:
        page_download("None", {}, True)


def kotobati(request):
    for i in range(1, 3, 1):
        url = f"https://www.kotobati.com/"
        respons = requests.get(url, verify=True, headers=headers)
        respons.raise_for_status()
        soup = BeautifulSoup(respons.content, "html.parser")
        books = soup.find_all("div", {"class": "book-teaser"})

        for book in books:
            book_url = book.find("h3").find("a")["href"]
            path = f"https://www.kotobati.com{book_url}"
            getItem(path)
            time.sleep(5)
    return JsonResponse({"message": "Scraped Successfully..."})
