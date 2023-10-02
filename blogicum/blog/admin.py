from django.contrib import admin

from .models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "is_published",
        "text",
        "created_at",
        "pub_date",
        "location",
        "category",
    )
    list_editable = (
        "is_published",
        "location",
        "category",
    )
    search_fields = ("title",)
    list_filter = ("category",)
    list_display_links = ("title",)
    empty_calue_display = "Не задано"


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ("title",)


class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ("name",)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
