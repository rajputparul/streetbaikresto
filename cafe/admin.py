from django.contrib import admin
import cloudinary.uploader

from .models import (
    GalleryItem,
    MenuItem,
    Message,
    NotificationLog,
    Order,
    Reservation,
    Review,
)


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "media_type",
        "active",
        "sort_order",
        "created_at",
    )
    list_editable = (
        "active",
        "sort_order",
    )
    list_filter = (
        "media_type",
        "active",
    )
    search_fields = (
        "title",
    )
    actions = (
        "delete_selected",
    )

    fieldsets = (
        (
            "Gallery Information",
            {
                "fields": (
                    "title",
                    "media_type",
                    "active",
                    "sort_order",
                )
            },
        ),
        (
            "Photo Upload",
            {
                "fields": (
                    "image_upload",
                )
            },
        ),
        (
            "Video Upload",
            {
                "fields": (
                    "video_upload",
                )
            },
        ),
    )

    def delete_model(self, request, obj):
        self._delete_cloudinary_file(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self._delete_cloudinary_file(obj)
        super().delete_queryset(request, queryset)

    @staticmethod
    def _delete_cloudinary_file(obj):
        try:
            if obj.media_type == "photo" and obj.image_upload:
                public_id = getattr(
                    obj.image_upload,
                    "public_id",
                    None,
                )
                if public_id:
                    cloudinary.uploader.destroy(
                        public_id,
                        resource_type="image",
                    )

            elif obj.media_type == "video" and obj.video_upload:
                public_id = getattr(
                    obj.video_upload,
                    "public_id",
                    None,
                )
                if public_id:
                    cloudinary.uploader.destroy(
                        public_id,
                        resource_type="video",
                    )
        except Exception:
            # Never block Django Admin deletion if Cloudinary cleanup fails.
            pass


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "diet",
        "bestseller",
        "active",
    )
    list_editable = (
        "price",
        "bestseller",
        "active",
    )
    list_filter = (
        "category",
        "diet",
        "bestseller",
        "active",
    )
    search_fields = (
        "name",
        "description",
    )


admin.site.register(
    [
        Order,
        Reservation,
        Review,
        Message,
        NotificationLog,
    ]
)
