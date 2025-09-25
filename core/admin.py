import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Event, Blog, Category, Publication, PhotoCategory, Photo, Video, VideoCategory, AboutPage, FAQ, \
    WhyUsImage, Service, PublicationCategory, PortfolioCategory, Portfolio, PortfolioImage, NewsletterSubscriber, ContactMessage


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ( "name",)
    search_fields = ("name",)

@admin.register(PublicationCategory)
class PublicationCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name",)

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "content")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "venue", "has_gallery_link")
    list_filter = ("date",)
    search_fields = ("title", "venue", "description")

    def has_gallery_link(self, obj):
        return bool(obj.gallery_link)
    has_gallery_link.boolean = True
    has_gallery_link.short_description = "Gallery?"


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content", "author__username")
    list_filter = ("created_at", "author")

    class Media:
        js = ('js/blog_preview.js',)

@admin.register(PhotoCategory)
class PhotoCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at")
    list_filter = ("category",)


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at")
    list_filter = ("category",)


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1

class WhyUsImageInline(admin.StackedInline):
    model = WhyUsImage
    extra = 0

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [FAQInline, WhyUsImageInline]
    list_display = ("title",)

admin.site.register(FAQ)
admin.site.register(WhyUsImage)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "number", "slug")
    prepopulated_fields = {"slug": ("title",)}  # Auto-generate slug from title
    search_fields = ("title", "description")
    ordering = ("number",)


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 3  # show 3 empty slots by default


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "client", "project_date", "created_at")
    list_filter = ("category", "project_date")
    search_fields = ("title", "client", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PortfolioImageInline]

@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "image", "alt_text")




def export_selected_csv(modeladmin, request, queryset):
    """
    Export only selected subscribers as CSV
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="selected_subscribers.csv"'

    writer = csv.writer(response)
    writer.writerow(["Email", "Subscribed At"])
    for subscriber in queryset:
        writer.writerow([subscriber.email, subscriber.subscribed_at])
    return response


export_selected_csv.short_description = "Export selected subscribers to CSV"


def export_all_csv(modeladmin, request, queryset):
    """
    Export ALL subscribers as CSV (ignores selection)
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="all_subscribers.csv"'

    writer = csv.writer(response)
    writer.writerow(["Email", "Subscribed At"])
    for subscriber in NewsletterSubscriber.objects.all().order_by("-subscribed_at"):
        writer.writerow([subscriber.email, subscriber.subscribed_at])
    return response


export_all_csv.short_description = "Export ALL subscribers to CSV"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at")
    search_fields = ("email",)
    list_filter = ("subscribed_at",)
    ordering = ("-subscribed_at",)
    actions = [export_selected_csv, export_all_csv]  # ✅ both options in Actions dropdown

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_filter = ("created_at",)
    ordering = ("-created_at",)