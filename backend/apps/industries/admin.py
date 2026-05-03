from django.contrib import admin

from .models import Industry, Keyword


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("industry", "term", "weight", "is_active")
    list_filter = ("industry", "is_active")
    search_fields = ("term",)
