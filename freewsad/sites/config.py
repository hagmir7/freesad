from base64 import encode
import re
import requests
from urllib.request import urlopen
import random
import string
import unicodedata
import time
import traceback
import sys
import os


from urllib.parse import urlparse


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


def download_file(url, local_filename):
    # Send a HTTP GET request to the specified URL
    with requests.get(url, stream=True) as r:
        # Raise an error for bad status codes
        r.raise_for_status()
        # Open a local file for writing in binary mode
        with open(local_filename, "wb") as f:
            # Write the file in chunks
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def extract_base_url(url):
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    return base_url


def get_file_size(file_path):
    """
    Get the size of the file in bytes.
    """
    return os.path.getsize(file_path)


def format_size(bytes):
    """
    Convert a file size in bytes into a human-readable format.
    """
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024


def generate_slug(text):
    # Normalize the text to ensure consistent encoding
    text = unicodedata.normalize("NFKD", text)
    # Convert text to lowercase
    text = text.lower()
    # Replace spaces and special characters with hyphens
    text = re.sub(r"\s+", "-", text)
    # Remove any non-alphanumeric characters except hyphens
    text = re.sub(r"[^\w-]", "", text)
    # Remove any leading or trailing hyphens
    text = text.strip("-")
    return text
