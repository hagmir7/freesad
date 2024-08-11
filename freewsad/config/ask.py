from openai import OpenAI
import os
from django.conf import settings


OPENAI_API_KEY = settings.AI_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def get_author(book_name):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an SEO assistant, And you know evrything about books I will give you a name of the book and give me a name of ther author, return just the author name",
            },
            {
                "role": "user",
                "content": book_name,
            },
        ],
    )

    return list(list(completion.choices[0].message)[0])[1]


def descripiton_generate(description):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """ 
                You are an SEO assistant, 
                And you know evrything about books 
                I will give complecate description
                - rewrit it better one and clean it inside HTML, (Just html tags needed without head and body)
                - do not return it in html block code, return it as string html
                - make descriptin more long thane 500 charactor
                - if there is h1 tags remove it
                 and return only HTML""",
            },
            {
                "role": "user",
                "content": description,
            },
        ],
    )

    return list(list(completion.choices[0].message)[0])[1]


def get_metakeyword(book_name):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an SEO assistant, And you know evrything about books I will give you a name of the book and give meta keywords, return just meta keywords by comma,",
            },
            {
                "role": "user",
                "content": book_name,
            },
        ],
    )

    return list(list(completion.choices[0].message)[0])[1]


def get_metadescription(book_name):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an SEO assistant, And you know evrything about books I will give you a name of the book and give meta description, return just meta description less than 160 charator",
            },
            {
                "role": "user",
                "content": book_name,
            },
        ],
    )

    return list(list(completion.choices[0].message)[0])[1]


# # # Save the response to a text file
# with open("book_summary.txt", "w") as file:
#     file.write(content)

# print("Summary saved to book_summary.txt")
