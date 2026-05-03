from django.contrib import admin

from .models import CollectionRun, ContentItem, CuratedChannel, Source, TrendKeyword


@admin.register(CuratedChannel)
class CuratedChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "handle", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "handle")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "type", "is_active")
    list_editable = ("is_active",)
    list_filter = ("type", "is_active")


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "published_at", "is_pinned")
    list_filter = ("source", "industries", "is_pinned")
    search_fields = ("title", "url")
    filter_horizontal = ("industries",)
    date_hierarchy = "published_at"


@admin.register(TrendKeyword)
class TrendKeywordAdmin(admin.ModelAdmin):
    list_display = ("rank", "keyword", "source", "observed_at")
    list_filter = ("source", "industries")


@admin.register(CollectionRun)
class CollectionRunAdmin(admin.ModelAdmin):
    list_display = ("source", "started_at", "finished_at", "status", "items_collected")
    list_filter = ("status", "source")
    readonly_fields = ("started_at", "finished_at")
