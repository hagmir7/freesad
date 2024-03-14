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

def slug(length=8):
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def remove_spaces_and_lines(string):
    return "".join(string.split()).replace("\n", "")


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
        # response.raise_for_status()

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
        # response.raise_for_status()

        file_temp = NamedTemporaryFile()
        file_temp.write(response.content)
        file_temp.flush()

        post = Book.objects.get(id=id)
        with open(file_temp.name, "rb") as file:
            post.file.save("file.pdf", File(file))
        print("File saved successfully.")
    else:
        print("Failed to download the file.")


def page_download(data):

    response = requests.get(data.get("pdf"), verify=True, headers=headers)
    if response.status_code == 200:
        response.raise_for_status()

        file_temp = NamedTemporaryFile()
        file_temp.write(response.content)
        file_temp.flush()

        if BookCategory.objects.filter(name__icontains=data.get("category")).exists():
            category = BookCategory.objects.filter(name__icontains=data.get("category"))[0]
        else:
            category = BookCategory.objects.create(
                name=data.get("category"),
                language=Language.objects.get(code=data.get("language")),
            )

        if not Book.objects.filter(name__icontains=data.get("name")):
            book = Book.objects.create(
                name=str(data.get("name")),
                title=f"Download {data.get('name')} Free PDF Book",
                user=User.objects.get(id=1),
                author=str(data.get("author")),
                language=Language.objects.get(code=data.get("language")),
                description=str(data.get("body")),
                tags=str(data.get('tags')),
                category=category,
                is_public=True,
            )
            download_image(data.get("image"), book.id)
            download_file(data.get("pdf"), book.id)
            time.sleep(5)


def zpdf(request):

    if request.GET.get("start"):
        start = int(request.GET.get("start"))
    else:
        return JsonResponse({"message": "Please we need start page"})

    for i in range(start, 10471+1, 1):
        try:
            url = f"https://www.z-pdf.com/book/{i}"
            respons = requests.get(url, verify=True, headers=headers)
            respons.raise_for_status()
            soup = BeautifulSoup(respons.content, "html.parser")

            name = remove_hashtags(
                delete_word(
                    delete_word(soup.find("h1").text, "Free PDF Download"),
                    "Free ePub Download",
                )
            )
            image = "https://www.z-pdf.com" + str(soup.find("div", {"class": "book-cover"}).find("img")['src'])
            body = soup.find("div", {"class": "book-description"})
            author = soup.find("a", {"itemprop": "author"}).text
            language = remove_spaces_and_lines(soup.find_all("tr")[6].find_all("td")[1].text)
            category = remove_extra_spaces(delete_word(soup.find_all("tr")[1].find_all("td")[1].find("a").text, "Books"))
            pdf = "https://www.z-pdf.com" + soup.find('a', {'class': "download-link"})['href']
            tags = remove_extra_spaces(soup.find_all("tr")[5].find_all("td")[1].text)

            data = {
                "image": image,
                "name": name,
                "category": category,
                "author": author,
                "language": language,
                "body": body,
                "pdf": pdf,
                "tags": tags
            }
            page_download(data)
            print("Book Create successfully ==>", name)
        except Exception as e:
            print("An error occurred ==> ", e)

    return JsonResponse({"message": "Scraped Successfully..."})
