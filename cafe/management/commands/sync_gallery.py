import os

import cloudinary.uploader

from django.conf import settings
from django.core.management.base import BaseCommand

from cafe.models import GalleryItem


class Command(BaseCommand):
    help = "Upload existing static gallery photos/videos to Cloudinary and create GalleryItem records."

    PHOTOS = [
        "burger.jpg",
        "chicken-category.jpg",
        "fries.jpg",
        "shawarma.jpg",
        "mojito.jpg",
        "drinks-category.jpg",
        "photo/about.jpg",
        "photo/2.jpg",
        "photo/3.webp",
    ]

    VIDEOS = [
        "photo/video/WhatsApp Video 2026-08-06 at 9.54.03 PM.mp4",
        "photo/video/WhatsApp Video 2026-08-06 at 9.54.02 PM.mp4",
        "photo/video/WhatsApp Video 2026-08-06 at 9.54.01 PM.mp4",
    ]

    def handle(self, *args, **options):
        static_dir = os.path.join(
            settings.BASE_DIR,
            "static",
            "images",
        )

        self.stdout.write(
            self.style.WARNING(
                "Starting Street Baik gallery sync..."
            )
        )

        photo_order = 0

        # -------------------------
        # PHOTOS
        # -------------------------
        for relative_path in self.PHOTOS:
            file_path = os.path.join(
                static_dir,
                relative_path,
            )

            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(
                        f"Photo not found: {relative_path}"
                    )
                )
                continue

            title = (
                os.path.splitext(
                    os.path.basename(relative_path)
                )[0]
                .replace("-", " ")
                .replace("_", " ")
                .title()
            )

            existing = GalleryItem.objects.filter(
                title=title,
                media_type="photo",
            ).first()

            if existing and existing.image_upload:
                self.stdout.write(
                    f"Already exists: {title}"
                )
                photo_order += 1
                continue

            self.stdout.write(
                f"Uploading photo: {relative_path}"
            )

            result = cloudinary.uploader.upload(
                file_path,
                folder="streetbaik/gallery/photos",
                resource_type="image",
                use_filename=True,
                unique_filename=True,
            )

            item = existing or GalleryItem()

            item.title = title
            item.media_type = "photo"
            item.image_upload = result["public_id"]
            item.video_upload = None
            item.active = True
            item.sort_order = photo_order

            item.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Uploaded photo: {title}"
                )
            )

            photo_order += 1

        # -------------------------
        # VIDEOS
        # -------------------------
        video_order = 100

        for relative_path in self.VIDEOS:
            file_path = os.path.join(
                static_dir,
                relative_path,
            )

            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(
                        f"Video not found: {relative_path}"
                    )
                )
                continue

            filename = os.path.basename(relative_path)

            title = (
                os.path.splitext(filename)[0]
                .replace("_", " ")
                .replace("-", " ")
                .title()
            )

            existing = GalleryItem.objects.filter(
                title=title,
                media_type="video",
            ).first()

            if existing and existing.video_upload:
                self.stdout.write(
                    f"Already exists: {title}"
                )
                video_order += 1
                continue

            self.stdout.write(
                f"Uploading video: {relative_path}"
            )

            file_size = os.path.getsize(file_path)

            if file_size > 100 * 1024 * 1024:
                result = cloudinary.uploader.upload_large(
                    file_path,
                    folder="streetbaik/gallery/videos",
                    resource_type="video",
                    use_filename=True,
                    unique_filename=True,
                    chunk_size=20 * 1024 * 1024,
                )
            else:
                result = cloudinary.uploader.upload(
                    file_path,
                    folder="streetbaik/gallery/videos",
                    resource_type="video",
                    use_filename=True,
                    unique_filename=True,
                )

            item = existing or GalleryItem()

            item.title = title
            item.media_type = "video"
            item.image_upload = None
            item.video_upload = result["public_id"]
            item.active = True
            item.sort_order = video_order

            item.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Uploaded video: {title}"
                )
            )

            video_order += 1

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Gallery sync completed successfully!"
            )
        )

        self.stdout.write(
            f"Total Gallery Items: {GalleryItem.objects.count()}"
        )