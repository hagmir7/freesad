from base64 import encode
from bs4 import BeautifulSoup, Comment
from django.shortcuts import render, redirect, get_object_or_404
import re
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
from django.contrib import messages
from django.utils.translation import gettext as _
import traceback
import sys


def slug(length=8):
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def remove_spaces_and_lines(string):
    return "".join(string.split()).replace("\n", "")


def remove_extra_spaces_and_lines(text):
    # Split the text into lines
    lines = text.split("\n")
    # Remove empty lines and leading/trailing whitespaces
    lines = [line.strip() for line in lines if line.strip()]
    # Join the lines with a single space
    cleaned_text = " ".join(lines)
    return cleaned_text


def delete_word(sentence, word):
    return sentence.replace(word, "")


def remove_extra_spaces(string):
    return " ".join(string.split())


def remove_hashtags(string):
    pattern = r"\#\d+(\.\d+)?|\(\d+(\.\d+)?\)"
    return re.sub(pattern, "", string)


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

        book = Book.books.get(id=id)
        with open(file_temp.name, "rb") as file:
            book.image.save("image.png", File(file))
            print("File saved successfully.")
    else:
        print("Failed to download the file. =>", response.text)


def download_file(url, id):
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        response.raise_for_status()

        file_temp = NamedTemporaryFile()
        file_temp.write(response.content)
        file_temp.flush()

        book = Book.books.get(id=id)
        with open(file_temp.name, "rb") as file:
            book.file.save("file.pdf", File(file))
            print("File saved successfully.")
    else:
        print("Failed to download the file. =>", response.text)


def page_download(data):
    if not data.get("pdf"):
        print("There is not PDF 📕❌")
    else:
        print("There is a PDF ✅")
        response = requests.get(data.get("pdf"), verify=True, headers=headers)
        if response.status_code == 200:
            response.raise_for_status()

            file_temp = NamedTemporaryFile()
            file_temp.write(response.content)
            file_temp.flush()
        else:
            print("Error To download File => ", response.status_code)

    if BookCategory.objects.filter(name__icontains=data.get("category")).exists():
        category = BookCategory.objects.filter(
            name__icontains=data.get("category")
        )[0]
    else:
        category = BookCategory.objects.create(
            name=data.get("category"),
            language=Language.objects.get(code="en"),
        )

    if not Book.books.filter(name__icontains=data.get("name")):
        book = Book.books.create(
            name=remove_extra_spaces(
                str(data.get("name")).replace("Download ", "").replace(" PDF", "").replace(" )", ")")
            ),
            title=f"{remove_extra_spaces(str(data.get('name')))} (Free PDF Book)",
            user=User.objects.get(id=1),
            author=remove_extra_spaces(str(data.get("author"))),
            language=Language.objects.get(code="en"),
            description=remove_extra_spaces_and_lines(str(data.get("body"))),
            body=str(data.get("body")),
            tags=str(data.get("tags")),
            category=category,
            is_public=True,
        )
        download_image(data.get("image"), book.id)
        print(data.get("pdf"))
        if data.get("pdf"):
            download_file(data.get("pdf"), book.id)


# Max 12019 - 17 - 05 - 2024
def dpdf(request):

    if request.GET.get("start"):
        start = int(request.GET.get("start"))
    else:
        return JsonResponse({"message": "Please we need start page"})

    for i in range(start, 0, -1):
        url = f"https://d-pdf.com/books/page/{i}"
        print("Page ===> ", i)
        respons = requests.get(url, verify=True, headers=headers)
        respons.raise_for_status()
        soup = BeautifulSoup(respons.content, "html.parser")

        books = soup.find_all("div", {"class": "book"})

        for book in books:

            url = f"https://www.d-pdf.com{book.find('a')['href']}"
            name = book.find("div", {"class": "book-info"}).find("a").text

            try:
                respons = requests.get(url, verify=True, headers=headers)
                respons.raise_for_status()
                soup = BeautifulSoup(respons.content, "html.parser")

                name = remove_hashtags(
                    delete_word(
                        delete_word(name, "Free PDF Download"),
                        "Free ePub Download",
                    )
                    .replace("(PDF DOWNLOAD)", "")
                    .replace("(PDF DOWNLOAD) ", "")
                    .replace("PDF Download", "")
                    .replace(" )", ")")
                    .replace("PDF", "")
                    .replace("Download", "")
                    .replace("( DOWNLOAD)", "")
                )
                image = "https://www.d-pdf.com" + str(
                    soup.find("div", {"class": "book-cover"}).find("img")["src"]
                )
                print(
                    "Image file => ",
                    str(soup.find("div", {"class": "book-cover"}).find("img")["src"]),
                )
                body = soup.find("div", {"class": "book-description"})
                author = soup.find("a", {"itemprop": "author"}).text
                language = remove_spaces_and_lines(
                    soup.find_all("tr")[6].find_all("td")[1].text
                )
                category = remove_extra_spaces(
                    delete_word(
                        soup.find_all("tr")[1].find_all("td")[1].find("a").text, "Books"
                    )
                )
                try:
                    pdf = (
                        "https://www.d-pdf.com"
                        + soup.find("a", {"class": "download-link"})["href"]
                    )
                except:
                    pdf = None
                tags = remove_extra_spaces(soup.find_all("tr")[6].find_all("td")[1].text)

                data = {
                    "image": image,
                    "name": str(name),
                    
                    "category": category,
                    "author": author,
                    "language": language,
                    "body": body,
                    "pdf": pdf,
                    "tags": tags,
                }
                page_download(data)
                print("Book Create successfully ==>", name)
            except Exception as e:
                print("An error occurred ==> ", e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                filename = exc_tb.tb_frame.f_code.co_filename
                line_num = exc_tb.tb_lineno
                print("File:", filename)
                print("Line:", line_num)
                print(url)

    return JsonResponse({"message": "Scraped Successfully..."})



