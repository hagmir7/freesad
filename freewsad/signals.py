import os
from django.conf import settings
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import Video, Quality, Post, Book
import fitz
from ebooklib import epub
# from moviepy.editor import VideoFileClip
from django.core.exceptions import ValidationError

# ----------- Utilities -----------


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def get_video_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        print("Error getting file size:", e)
        return 0


def format_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"


def epub_count_pages(epub_path):
    try:
        book = epub.read_epub(epub_path)
        return len(book.spine)
    except Exception as e:
        print("Error reading EPUB:", e)
        return 1


def get_quality(width, height):
    if width >= 7680 and height >= 4320:
        return "8K Ultra HD"
    elif width >= 3840 and height >= 2160:
        return "4K Ultra HD"
    elif width >= 2560 and height >= 1440:
        return "1440p Quad HD"
    elif width >= 1920 and height >= 1080:
        return "1080p Full HD"
    elif width >= 1280 and height >= 720:
        return "720p HD"
    elif width >= 852 and height >= 480:
        return "480p SD"
    else:
        return f"{height}p SD"


def get_real_file_path(instance_file):
    if settings.CPANEL:
        return os.path.normpath(f"/home/agha6919/freesad/{instance_file.url}")
    return instance_file.path


# ----------- Post Model Signals -----------


@receiver(pre_save, sender=Post)
def delete_post_old_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            existing = sender.objects.get(pk=instance.pk)
            if existing.image and existing.image != instance.image:
                existing.image.delete(save=False)
        except sender.DoesNotExist:
            pass


@receiver(pre_delete, sender=Post)
def delete_post_image_file(sender, instance, **kwargs):
    try:
        instance.image.delete(save=False)
    except Exception as e:
        print("Error deleting post image:", e)


# ----------- Book Model Signals -----------


@receiver(pre_save, sender=Book)
def delete_book_old_files(sender, instance, **kwargs):
    if instance.pk:
        try:
            existing = sender.objects.get(pk=instance.pk)
            if existing.image and existing.image != instance.image:
                existing.image.delete(save=False)
            if existing.file and existing.file != instance.file:
                existing.file.delete(save=False)
        except sender.DoesNotExist:
            pass


@receiver(pre_delete, sender=Book)
def delete_book_files(sender, instance, **kwargs):
    try:
        if instance.image:
            instance.image.delete(save=False)
        if instance.file:
            instance.file.delete(save=False)
    except Exception as e:
        print("Error deleting book files:", e)


@receiver(post_save, sender=Book)
def update_book_page_count(sender, instance, created, **kwargs):
    if instance.file and not instance.pages:
        try:
            pages = 1
            if instance.book_type == "PDF":
                doc = fitz.open(instance.file.path)
                pages = doc.page_count
                doc.close()
            elif instance.book_type == "EPUB":
                pages = epub_count_pages(instance.file.path)

            size_mb = round(instance.file.size * 1e-6, 2)
            size_str = (
                f"{size_mb} MB"
                if size_mb >= 1
                else f"{round(instance.file.size * 0.001, 2)} KB"
            )

            Book.objects.filter(pk=instance.pk).update(pages=pages, size=size_str)
        except Exception as e:
            print("Error processing book file:", e)


# ----------- Video Model Signals -----------


@receiver(pre_save, sender=Video)
def delete_video_old_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            existing = sender.objects.get(pk=instance.pk)
            if existing.image and existing.image != instance.image:
                existing.image.delete(save=False)
        except sender.DoesNotExist:
            pass


@receiver(pre_delete, sender=Video)
def delete_video_image(sender, instance, **kwargs):
    try:
        instance.image.delete(save=False)
    except Exception as e:
        print("Error deleting video image:", e)


# ----------- Quality Model Signals -----------


@receiver(pre_save, sender=Quality)
def delete_quality_old_file(sender, instance, **kwargs):
    if instance.pk:
        try:
            existing = sender.objects.get(pk=instance.pk)
            if existing.file and existing.file != instance.file:
                existing.file.delete(save=False)
        except sender.DoesNotExist:
            pass


@receiver(pre_delete, sender=Quality)
def delete_quality_file(sender, instance, **kwargs):
    try:
        if instance.file:
            instance.file.delete(save=False)
    except Exception as e:
        print("Error deleting quality file:", e)


@receiver(post_save, sender=Quality)
def create_quality_info(sender, instance, created, **kwargs):
    if created and instance.file:
        try:
            file_path = get_real_file_path(instance.file)
            # video = VideoFileClip(file_path)
            width, height = video.size
            duration = format_duration(video.duration)
            size = format_size(get_video_file_size(file_path))
            quality_str = get_quality(width, height)
            video.close()

            # Prevent duplicate quality for the same video
            if instance.video.video_qualities.filter(quality=quality_str).exists():
                instance.file.delete(save=False)
                instance.delete()
                raise ValidationError("Quality already exists for this video.")

            Quality.objects.filter(pk=instance.pk).update(
                width=width,
                height=height,
                duration=duration,
                size=size,
                quality=quality_str,
            )

        except Exception as e:
            print("Error processing video quality:", e)
