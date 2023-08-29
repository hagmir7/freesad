import requests
from bs4 import BeautifulSoup

import re
from freewsad.models import Book, BookCategory, Author
from django.http import JsonResponse
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.models import User
import os
from freewsad.models import Language


# Regular expression pattern to match the text inside parentheses
pattern = r'\((.*?)\)'

proxy = {"http": "http://10.122.53.36:8080",
         "https": "http://10.122.53.36:8080"}

# Remove end spaces


def remove_end_spaces(string):
    return "".join(string.rstrip())

# Remove first and  end spaces


def remove_first_end_spaces(string):
    return "".join(string.rstrip().lstrip())

# Remove all spaces


def remove_all_spaces(string):
    return "".join(string.split())

# Remove all extra spaces


def remove_all_extra_spaces(string):
    return " ".join(string.split())


def download_file(url, id, model, file=None):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            response.raise_for_status()

            file_temp = NamedTemporaryFile()
            file_temp.write(response.content)
            file_temp.flush()

            if model == 'author':
                instance = Author.objects.get(id=id)  # Instantiate your model object
            else:
                instance = Book.objects.get(id=id)  # Instantiate your model object

            with open(file_temp.name, 'rb') as file:
                instance.image.save("image.png", File(file))

            print("File saved successfully.")
        else:
            print("Failed to download the file.")
    except:
        pass


def download_book(url, id):
    response = requests.get(url)
    if response.status_code == 200:
        response.raise_for_status()

        file_temp = NamedTemporaryFile()
        file_temp.write(response.content)
        file_temp.flush()

        instance = Book.objects.get(id=id)

        with open(file_temp.name, 'rb') as file:
            instance.file.save("file.pdf", File(file))

        print("File saved successfully.")
    else:
        print("Failed to download the file.")




def getAuthor(url, author_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find('div', {'class': 'v-blog-wrap'})
    image = content.find('img')['src']
    description = content.find('div', {'class': 'show-less-div'}).find_all('p')[1].text

    if not Author.objects.filter(full_name=author_name).exists():
        author = Author.objects.create(
            full_name = author_name,
            description = description
        )
        download_file(image, author.id, "author")
        return author
    else:
        return Author.objects.filter(full_name=author_name)[0]



def getItem(url, image, name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find('div', {'class': 'row'})
    info = soup.find('ul', {'class': 'v-list'})
    try:
        author = info.find_all('li')[8].find('a').text
        author_url = info.find_all('li')[8].find('a')['href']
    except:
        author = info.find_all('li')[7].find('a').text
        author_url = info.find_all('li')[7].find('a')['href']

    lang = info.find_all('li')[0].find('a').text

    category = info.find_all('li')[1].find('a').text
    title = soup.find('h1').text
    body = soup.find('div', {'class': 'body-texdt'})
    download = soup.find('a', {'class': 'v-btn-default'})['href']

    
    getAuthor(author_url, author)

    # Create category

    if not BookCategory.objects.filter(name=category).exists():
        new_category = BookCategory.objects.create(
            name = category
        )
    else:
        new_category = BookCategory.objects.get(name=category)



    if lang == 'العربية':
        language = Language.objects.get(code='ar')
    else:
        language = Language.objects.get(code='en')



    book = Book.objects.create(
        user= User.objects.get(id=1),
        name=str(name),
        title=str(title),
        description=str(body),
        tags = f"{name}, {title}",
        category = new_category,
        language = language
        
        
    )
    download_file(image, book.id, 'book')
    download_book(download, book.id)

def books(request):
    for page in range(5, 0, -1):
        url = f"https://foulabook.com/ar/books?page={page}/"
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")
        results = soup.find_all("li", {'class': 'related-item'})
        print(f"Page ==== {page}")
        for item in results:
            if item:
                link = item.find('a')['href']
                try:
                    image = item.find('img')['src']
                except:
                    image = None
                name = item.find('a', {'rel': 'bookmark'}).text
                getItem(link, image, name)


    return JsonResponse({"message": "Compoletd"})
