from base64 import encode
from bs4 import BeautifulSoup
import requests
from freewsad.models import Post, Language, PostCategory
from django.http import JsonResponse







proxy ={"http": "http://10.122.53.36:8080", "https": "http://10.122.53.36:8080"}

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




def getItem(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    article = soup.find('div', {'class': 'article-content'})
    try:
        article.find('figure', {'class': 'wp-block-embed'}).decompose()
    except:
        pass

    try:
        for item in article.find_all('a', {'class': 'aal_anchor'}):
            article.find('a', {'class': 'aal_anchor'}).decompose()
    except:
        pass

    try:
        article.find('div', {'class': 'in-article-cards'}).decompose()
    except:
        pass


    
    return article


def dev(request):
    for page in range(1, 200):
        url = f"https://css-tricks.com/archives/page/{page}/"
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")
        results = soup.find_all("article", {'class': 'article-card'})
        print(f"Page ==== {page}")
        for item in results:
            if item:
                title = remove_all_extra_spaces(item.find('h2').text)
                # Image
                try: image = item.find('img', {'class': 'article-thumbnail wp-post-image'})['src']
                except: image = None
                # Link
                
                # Tags
                try: tags = ','.join([x.text for x in item.find_all('a', {'rel': 'tag'})])
                except: tags = ''
                description = str(item.find('div', {'class': "card-content"}).text)[0:150]

                
                try:
                    link = item.find('div', {'class': 'article-thumbnail-wrap'}).find('a')['href']
                    if not Post.objects.filter(title=title).exists() and description != None:
                        Post.objects.create(
                            title = str(title),
                            imageURL = str(image),
                            tags = str(tags),
                            description = str(description),
                            language = Language.objects.get(id=1),
                            category = PostCategory.objects.get(id=1),
                            body = str(getItem(link))
                        )
                        print('Success...')
                    print("--------------------------------------------")
                except:
                    print("------ Error")
          
    return JsonResponse({'message': 'Scraped Successfully...'})
