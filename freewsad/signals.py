from .models import Video, Quality, Post, Book
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
import fitz
from ebooklib import epub
from moviepy.editor import VideoFileClip
import os
from django.conf import settings

# Format video duration
def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Get video file size
def get_video_file_size(file_path):
    try:
        file_size = os.path.getsize(file_path)
        return file_size
    except Exception as e:
        print("Error:", str(e))
        return None

# Format video file size
def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

# Count edub book page
def epub_count_pages(epub_path):
    book = epub.read_epub(epub_path)
    num_pages = len(book.spine)

    return num_pages


@receiver(pre_save, sender=Post)
def delete_post_old_image(sender, instance, **kwargs):
    if instance.pk:
        # Retrieve the existing instance from the database
        existing_instance = sender.objects.get(pk=instance.pk)

        # Check if the image field has changed
        if existing_instance.image and existing_instance.image != instance.image:
            # Delete the old image file
            existing_instance.image.delete(save=False)


@receiver(pre_delete, sender=Post)
def delete_post_image_file(sender, instance, **kwargs):
    # Delete the image file when the model instance is deleted
    instance.image.delete(save=False)


@receiver(pre_save, sender=Book)
def delete_book_old_image(sender, instance, **kwargs, ):
    if instance.pk:
        # Retrieve the existing instance from the database
        existing_instance = sender.objects.get(pk=instance.pk)

        # Check if the image field has changed
        if existing_instance.image and existing_instance.image != instance.image:
            # Delete the old image file
            existing_instance.image.delete(save=False)

        if existing_instance.file and existing_instance.file != instance.file:
            # Delete the old file file
            existing_instance.file.delete(save=False)


@receiver(pre_delete, sender=Book)
def delete_book_image_file(sender, instance, **kwargs):
    # Delete the image file when the model instance is deleted
    instance.image.delete(save=False)
    instance.file.delete(save=False)


@receiver(post_save, sender=Book)
def update_page_count(sender, instance, **kwargs):

    if instance.file and not instance.pages:
        if instance.book_type == "PDF":
            doc = fitz.open(instance.file.path)
            instance.pages = doc.page_count
            doc.close()

        elif instance.book_type == "EPUB":
            instance.pages = epub_count_pages(instance.file.path)
        else:
            instance.pages = 1

        if round(instance.file.size * 1e-6, 3) >= 1:
            instance.size = str(round(instance.file.size * 1e-6, 2)) + " MB"
        else:
            instance.size = str(round(instance.file.size * 0.001, 2)) + " KB"
        instance.save()


@receiver(pre_delete, sender=Video)
def delete_video_image(sender, instance, **kwargs):
    # Delete the image file when the model instance is deleted
    instance.image.delete(save=False)


@receiver(pre_save, sender=Video)
def delete_video_old_image(sender, instance, **kwargs):
    if instance.pk:
        # Retrieve the existing instance from the database
        existing_instance = sender.objects.get(pk=instance.pk)

        if existing_instance.image and existing_instance.image != instance.image:
            # Delete the old image file
            existing_instance.image.delete(save=False)


def get_quality(width, height):
    if width >= 7680 and height >= 4320:
        return '8K Ultra HD'
    elif width >= 3840 and height >= 2160:
        return '4K Ultra HD'
    elif width >= 2560 and height >= 1440:
        return '1440p Quad HD'
    elif width >= 1920 and height >= 1080:
        return '1080p Full HD'
    elif width >= 1280 and height >= 720:
        return '720p HD'
    elif width >= 852 and height >= 480:
        return '480p SD'
    else:
        return f'{height}p SD'

@receiver(post_save, sender=Quality)
def create_quality(sender, instance, created, **kwargs):
    if created:
        if instance.file:
            if settings.CPANEL:
                file_path = os.path.normpath(f'/home/agha6919/freesad/{os.path.join(instance.file.url)}')
            else:
                file_path = os.path.normpath(f'{os.path.join(instance.file.url)}')
            video = VideoFileClip(file_path)
            width, height = video.size
            instance.width = width
            instance.height = height
            instance.duration = format_duration(video.duration)
            instance.size = format_size(get_video_file_size(file_path))
            instance.quality = get_quality(width, height)
            video.close()
            video_instance = instance.video

            # qualities = Quality.objects.filter(video=video_instance)
            # print(qualities)
            # if qualities:
            #     if not qualities[1].duration == instance.duration:
            #         instance.delete()
            #         raise ValueError("Quality is not the same")

            if video_instance.video_qualities.filter(quality=instance.quality).exists():
                instance.delete()
                raise ValueError("Quality already exists")
        
            instance.save()

@receiver(pre_delete, sender=Quality)
def delete_quality_file(sender, instance, **kwargs):
    # Ensure the file exists before attempting deletion
    if instance.file:
        instance.file.delete(save=False)


@receiver(pre_save, sender=Quality)
def delete_quality_old_image(sender, instance, **kwargs):
    if instance.pk:
        # Retrieve the existing instance from the database
        existing_instance = sender.objects.get(pk=instance.pk)

        # Check if the image field has changed
        if existing_instance.file and existing_instance.file != instance.file:
            # Delete the old file file
            existing_instance.file.delete(save=False)

from PIL import Image
from io import BytesIO

# @receiver(post_save, sender=Book)
# def resize_and_convert_to_webp(sender, instance, **kwargs):
#     # Check if the instance has an image field (adjust 'image' accordingly)
#     if hasattr(instance, 'image') and instance.image:
#         # Open the image using Pillow as specified
#         image_data = os.path.normpath(f'{os.path.join(instance.image)}')
#         img = Image.open(BytesIO(instance.image.read()))

#         if img.width > 400 or img.height > 300:
#             output_size = (400, 300)
#             img.thumbnail(output_size)

#             # Convert the image to WebP format
#             webp_path = instance.image.path.replace('.png', '.webp')  # Change the extension as needed
#             img.save(webp_path, 'WEBP', quality=85)  # You can adjust quality as needed

#             # Update the image field to the new WebP image
#             instance.image.name = webp_path.split('/')[-1]
#             instance.save()
