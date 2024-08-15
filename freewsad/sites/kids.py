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
    if("scholastic" not in url):
        url = "https://kids.scholastic.com" + url
    print(url)
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
                str(data.get("name"))
                .replace("Download ", "")
                .replace(" PDF", "")
                .replace(" )", ")")
            ),
            title=f"{remove_extra_spaces(str(data.get('name')))} (PDF Book)",
            user=User.objects.get(id=1),
            author=remove_extra_spaces(str(data.get("author"))),
            language=Language.objects.get(code="en"),
            description=remove_extra_spaces_and_lines(str(data.get("body"))),
            body=str(data.get("body")),
            tags="children's books, kids books, children's literature, books for kids, children's stories, picture books, early reader books, children's book reviews, kids book recommendations, educational books for kids, classic children's books, bedtime stories, kids reading",
            category=category,
            is_public=True,
        )
        download_image(data.get("image"), book.id)
        # download_file(data.get("pdf"), book.id)
        # time.sleep(5)
    else:
        print("Book already exists")


def kids(request):
    if request.GET.get("url"):
        url = request.GET.get("url")
    else:
        return JsonResponse({"message": "Please we need url page"})

    response = requests.get(url, verify=True, headers=headers)
    if response.status_code == 200:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        books = soup.find_all("div", {"class": "bookDetails__wrapper"})
        for book in books:
            book_image = book.find("img", class_="bookDetails__image")["src"]
            # series_name = book.find('p', class_='bookDetails__seriesName').text.strip()
            title = book.find("p", class_="bookDetails__title").text.strip()
            author = (
                book.find("p", class_="bookDetails__contributors--author")
                .text.replace("Author:", "")
                .replace(";", "")
                .replace("&nbsp", "")
                .strip()
            )
            genre = book.find("div", class_="bookDetails__genre").text.strip()
            description = book.find("p", class_="bookDetails__description").text.strip()
            data = {
                "image": book_image,
                "name": title,
                "category": genre,
                "author": author,
                "language": "en",
                "body": description,
            }
            page_download(data)
            print("Book Create successfully ==>", title)
    return JsonResponse({"message": "Scraped Successfully..."})
