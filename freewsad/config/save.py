from django.core.files.storage import FileSystemStorage
from PIL import Image
import fitz  # PyMuPDF
import random
from .ask import *
import string
import re
import unicodedata
from pathlib import Path

from django.http import HttpResponse
from django.conf import settings
import io
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def random_slug(length=8):
    characters = string.ascii_lowercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def remove_file(file_path):
    """Remove a file specified by file_path."""
    try:
        os.remove(BASE_DIR / file_path)
        print(f"File {BASE_DIR / file_path} removed successfully.")
    except OSError as e:
        print(f"Error removing file: {e}")


def format_size(size):
    """Format the size from bytes to a more readable form."""
    for unit in ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def get_file_size(file_path):
    """Get the size of a file specified by file_path."""
    try:
        size = os.path.getsize(file_path)
        formatted_size = format_size(size)
        print(f"File size of {file_path}: {formatted_size}")
        return formatted_size
    except OSError as e:
        print(f"Error getting file size: {e}")
        return None


def get_pdf_image(pdf_url, image_name):
    # Open the PDF file
    pdf_document = fitz.open(pdf_url)

    # Get the first page
    page = pdf_document.load_page(0)  # Page 0 is the first page

    # Render page to an image (you can specify the resolution here)
    pix = page.get_pixmap()

    # Convert to PIL image
    image = Image.open(io.BytesIO(pix.tobytes()))

    # Save the image in the media directory
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
    image.save(image_path)

    return image_path


def slug(name):
    """Generate a slug from a given name."""
    # Normalize the name to remove accents and special characters
    normalized = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )
    # Convert to lowercase and replace spaces/undesired characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower())
    # Remove leading and trailing hyphens
    return slug.strip("-")


def rename_file(old_name, new_name):
    """Rename a file from old_name to new_name."""
    try:
        os.rename(old_name, new_name)
        print(f"File renamed from {old_name} to {new_name}")
    except OSError as e:
        print(f"Error renaming file: {e}")


def get_pdf_info(pdf_path):
    """Extract information from a PDF file."""
    pdf_document = fitz.open(BASE_DIR / pdf_path)

    # Get the number of pages
    num_pages = pdf_document.page_count

    # Get metadata
    metadata = pdf_document.metadata

    if metadata.get("title"):
        metadata["author"] = get_author(metadata["title"])
        metadata["keywords"] = get_metakeyword(metadata["title"])
        metadata["subject"] = get_metadescription(metadata["title"])
        metadata["creator"] = "Freesad (https://freesad.com)"
        metadata["producer"] = "Freesad (https://freesad.com)"

        image_filename = f"{slug(metadata['title'])}.png"

        # Save PDF Image
        if settings.CPANEL:
            image_path = get_pdf_image(
                pdf_path, f"/home/agha6919/freesad.com/media/PDF-images/{image_filename}"
            )
        else:
            image_path = get_pdf_image(
                pdf_path, f"PDF-images/{image_filename}"
            )

        # Save PDF
        pdf_document.set_metadata(metadata)
        pdf_document.saveIncr()

        data = {
            "name": metadata["title"],
            "title" : f"Download {metadata['title']} Free PDF Book",
            "author": metadata["author"],
            "description": metadata["subject"],
            "keywords": metadata["keywords"],
            "image": image_path,
            "extantion": "PDF",
            "pages": num_pages,
            "slug": slug(metadata["title"]),
        }

        return data
    else:
        return False
