from base64 import encode
from bs4 import BeautifulSoup, Comment
import requests
from freewsad.models import Post, Language, PostCategory
from django.http import JsonResponse
from .robo import bot

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile






proxy ={"http": "http://10.122.53.36:8080", "https": "http://10.122.53.36:8080"}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

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





def download_file(url, id):
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            response.raise_for_status() 

            file_temp = NamedTemporaryFile()
            file_temp.write(response.content)
            file_temp.flush()

            post = Post.objects.get(id=id)  # Instantiate your model object
            with open(file_temp.name, 'rb') as file:
                post.image.save("image.png", File(file))
            print("File saved successfully.")
        else:
            print("Failed to download the file.")




def getItem(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    result = soup.find('div', {'class': 'entry-content'})

    # Check if result is not None before saving to file
    for script in result.find_all("script"):
        script.extract()

    for script in result.find_all("ins"):
        script.extract()


    # Remove unnecessary line breaks and empty elements
    for elem in result.find_all(['br', 'div']):
        elem.extract()

    # Remove comments
    for comment in result.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove any attributes that aren't needed (for example, style attributes)
    for tag in result.find_all():
        del tag['style']

    # Remove empty <div> elements
    for div in result.find_all('div'):
        if not div.text.strip():
            div.extract()

    # Replace non-semantic <br> elements with <p> or <div> as needed
    for br in result.find_all('br'):
        br.replace_with('\n')  # Replace <br> with newline character

    # Print the cleaned HTML

    p_tags = soup.find_all('p')

    # Iterate through <p> tags and remove those with child tags
    for p_tag in p_tags:
        first_child = p_tag.find(True)
        if first_child and first_child.name:
            p_tag.extract()

    return result.prettify()

def airlet(request):
    for page in range(200, 1, -1):
        url = f"https://www.airtel.in/blog/page/{page}/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('article', {'class' : 'bam-entry'})

        for article in articles:
            title = article.find('h2').text
            image = article.find('img')['src']
            path =  article.find('a')['href']
            if not Post.objects.filter(imageURL=str(title)).exists():
                post = Post.objects.create(
                    title = str(bot(f"Rewrite this title with better without &quot ({title})")),
                    imageURL = str(image),
                    tags = str(bot(f"Gave me eso meta keyword for ({title}) without &quot")),
                    description = str(bot(f"Gave me eso meta description for ({title}) without &quot")),
                    language = Language.objects.get(id=1),
                    category = PostCategory.objects.get(id=15),
                    body = str(getItem(path))
                )
                download_file(image, post.id)
    return JsonResponse({'message': 'Scraped Successfully...'})
