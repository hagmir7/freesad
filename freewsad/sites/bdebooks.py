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

from openai import OpenAI
import os
from django.conf import settings


OPENAI_API_KEY = settings.AI_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def get_description(book_name):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an SEO assistant, And you know evrything about books I will give you a name of the book and give me description about, return just descrption inside html",
            },
            {
                "role": "user",
                "content": book_name,
            },
        ],
    )

    return list(list(completion.choices[0].message)[0])[1]


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
                language=Language.objects.get(code="en"),
            )

        book = Book.books.create(
            name=remove_extra_spaces(str(data.get("name"))),
            title=f"Download {remove_extra_spaces(str(data.get('name')))} Free PDF Book",
            user=User.objects.get(id=1),
            author=remove_extra_spaces(str(data.get("author"))),
            language=Language.objects.get(code="en"),
            description=remove_extra_spaces_and_lines(str(data.get("body").text)),
            body=str(data.get("body")),
            tags=str(data.get("tags")),
            category=category,
            is_public=True,
        )
        download_image(data.get("image"), book.id)
        download_file(data.get("pdf"), book.id)
    else:
        print("Error Download file")


def get_item(url):
    response = requests.get(url, verify=True, headers=headers)
    if response.status_code == 200:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("h1").text
        if not Book.objects.filter(name=name).exists():
            image_url = soup.find("img", {"class": "attachment-post-thumbnail"})["srcset"].split(" ")[0]
            file_url = soup.find("ul", {"class": "sub_btns"}).find_all("a")[0]["href"]
            tags = soup.find("div", {"class": "single_book_page_header_genres"}).find_all('a')
            tags_string = ""
            for tag in tags:
                tags_string += f"{tag.text},"

            tags_string = tags_string.rstrip(',')

            author = soup.find("div", {"class": "single_book_author"}).find('a').text
            category = soup.find("div", {"class": "single_book_page_header_genres"}).find("a").text
            try:
                description = soup.find("div", {"class": "single_book_page_excerpt_inner"}).find("p")
            except:
                # Ask ai
                description = get_description(name)

            data = {
                "image": image_url,
                "name": name,
                "category": category,
                "author": author,
                "language": "en",
                "body": description,
                "pdf": file_url,
                "tags": tags,
            }
            page_download(data)
            print("Book Create successfully ==>", name)
        else:
            print("Book already exists")
    else:
        print("Request Error")


# Max 12019 - 17 - 05 - 2024
def bdebooks(request):
    for i in range(2, 700):
        page_url = f"https://bdebooks.com/en/popular-books/page/{i}"
        response = requests.get(page_url, verify=True, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        book_cards = soup.find_all("div", {"class", "ep_popular_post_item"})
        for card in book_cards:
            book_url = card.find('a')['href']
            get_item(book_url)




    return JsonResponse({"message": "Scraped Successfully..."})
