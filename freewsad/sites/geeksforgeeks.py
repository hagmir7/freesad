
from base64 import encode
from bs4 import BeautifulSoup
import requests
from freewsad.models import Post, Language, PostCategory
from django.http import JsonResponse

proxy ={"http": "http://10.122.6.127:8080", "https": "http://10.122.6.127:8080"}

def getItem(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    article = soup.find('div', {'class': 'text'})
    try: article.find('div', 'clear').decompose()
    except: pass
    for item in range(len(article.find_all('div', {"id": 'GFG_AD_Desktop_InContent_ATF_336x280'}))):
        article.find('div', {"id": 'GFG_AD_Desktop_InContent_ATF_336x280'}).decompose()

    for item in range(len(article.find_all('div', {'class':'code-gutter'}))):
        article.find('div', {'class':'code-gutter'}).decompose()

    for item in range(len(article.find_all('div', {'class':'code-output-container'}))):
        article.find('div', {'class':'code-output-container'}).decompose()
    return article

    

def getImage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    article = soup.find('div', {'class': 'text'})
    article.find('div', {'class': "clear"})
    try:
        image = article.find("img")['src']
    except:
        image = None
    return image


def geeksforgeeks(request):
    for page in range(100, 1, -1):
        print(f"===== Page {page}")
        url = f"https://www.geeksforgeeks.org/page/{page}/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("div", class_="articles-list_item")
        for item in results:
            if item:
                title = item.find('a').text
                link = item.find('a')['href']
                description = str(item.find('div', class_="text"))[0:150]
                tags = ','.join([x.text for x in item.find_all('div', {'class': 'item'})])
                body = getItem(link)
                image = getImage(link)
                if not Post.objects.filter(title=title).exists():
                    Post.objects.create(
                        title=str(title),
                        imageURL=str(image),
                        tags=str(tags),
                        description=str(description),
                        language=Language.objects.get(id=1),
                        category=PostCategory.objects.get(id=1),
                        body=str(body)
                    ) 
                    print("Successfully...")
    return JsonResponse({'message': 'Seuccessfully....'})
