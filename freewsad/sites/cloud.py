from base64 import encode
from bs4 import BeautifulSoup
import requests
from freewsad.models import Post, Language, PostCategory
from django.http import JsonResponse

proxy ={"http": "http://10.122.6.127:8080", "https": "http://10.122.6.127:8080"}

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


hdr = {'User-Agent': 'Mozilla/5.0'}

def getItem(url):
    response = requests.get(url, headers=hdr)
    soup = BeautifulSoup(response.content, "html.parser")
    article = soup.find('article').find('div',{'class':'o-rhythm--default'})
    return article



def cloud(request):
    for page in range(30, 1 , -1):
        print(f"Page === {page}")
        url = f"https://cloudfour.com/thinks/page/{page}/"
        page = requests.get(url, headers=hdr)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("article")
        for item in results:
            if item:
                title = remove_all_extra_spaces(item.find('a', {'class': 'c-card__link'}).text)
                link = item.find('a', {'class': 'c-card__link'})['href']
                description = remove_all_extra_spaces(str(item.find('p').text)[0:150])
                image = item.find('img')['src']
                print("--------------------------------------------------------------")
                if not Post.objects.filter(title=title).exists():
                    Post.objects.create(
                        title=str(title),
                        imageURL=str(image),
                        description=str(description),
                        language=Language.objects.get(id=1),
                        category=PostCategory.objects.get(id=1),
                        body=str(getItem(link))
                    )
                    print("Successfully...")
    return JsonResponse({'message': 'Seuccessfully....'})
