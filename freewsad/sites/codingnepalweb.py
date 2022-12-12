from base64 import encode
from bs4 import BeautifulSoup
import requests
from freewsad.models import Post, Language, PostCategory
from django.http import JsonResponse

proxy ={"http": "http://10.122.6.127:8080", "https": "http://10.122.6.127:8080"}
headers = {'User-Agent': 'Mozilla/5.0'}

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
    article = soup.find('article').find('div',{'class':'td-post-content'})
    description = article.find_all('p')[1].text


    try:
        for item in range(len(article.find_all('script'))):
            article.find('script').decompose()
    except:pass


    for item in range(len(article.find_all('ins'))):
        article.find('ins').decompose()

    for item in range(len(article.find_all('div', {'class': 'code-block'}))):
        article.find('div', {'class': 'code-block'}).decompose()

    try:
        for item in article.find_all('a'):
            # print(str(item['href'])[0:41])
            if str(item['href'])[0:41] != 'https://www.codingnepalweb.com/wp-content':
                item['href'] = str(item['href']).replace('www.codingnepalweb.com', 'www.freewsad.com/p')
    except: pass


    try:
        article.find('button').decompose()
    except: pass

    
    

    tags = soup.find('ul',{'class': 'td-tags'}).find_all('a')
    tags = ','.join([x.text for x in tags])



    return {
        'article': article,
        'tags' : tags,
        'description' : description
    }







def codingnepalweb(request):
    for page in range(13, 1, -1):
        url = f"https://www.codingnepalweb.com/page/{page}/"
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")
        results = soup.find_all("div", {'class': 'tdb_module_loop_2'})
        print(f'Page === {page}')
        for item in results:
            if item:
                title = item.find('h3', {'class': 'entry-title'}).text
                link = item.find('a', {'class': "td-image-wrap"})['href']
                slug = str(link).replace('https://www.codingnepalweb.com/', '').replace('/','')
                image = item.find('span', {'class': 'entry-thumb td-thumb-css'})['data-img-url']
                print('-------------------------------------------')
                if not Post.objects.filter(title=title).exists() and getItem(link):
                    Post.objects.create(
                        title = str(title)[0:149],
                        slug = str(slug),
                        imageURL = str(image),
                        tags = str(getItem(link).get('tags'))[0:149],
                        body = str(getItem(link).get('article')),
                        description = str(getItem(link).get('description')),
                        language = Language.objects.get(id=1),
                        category = PostCategory.objects.get(id=1)
                    )
                    print('Seved successfully...')

    return JsonResponse({'message': "Successfully..."})

