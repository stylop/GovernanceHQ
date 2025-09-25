import requests
import uuid
import urllib.request
from django.core.files.base import ContentFile
from urllib.parse import urlparse, parse_qs
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone


from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# models.py
from django.db import models
from django.utils.text import slugify

class PublicationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Publication Categories"

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Publication(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="publications/images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey("PublicationCategory",on_delete=models.SET_NULL,null=True,blank=True,related_name="publications")
    pdf_file = models.FileField(upload_to="publications/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Publication.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True,default="events/default.png")
    gallery_link = models.URLField(
        blank=True, null=True,
        help_text="Optional link to social media, Google Photos, etc."
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} @ {self.venue if self.venue else 'TBA'}"

class Blog(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="blogs",null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    image = models.ImageField(upload_to="blogs/", blank=True, null=True)
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # auto-generate slug if empty
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class PhotoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Photo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(PhotoCategory, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="gallery/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class VideoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Video(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, related_name="videos")

    # Either upload a file OR embed a YouTube/Vimeo link
    video_file = models.FileField(upload_to="videos/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    thumbnail = models.ImageField(upload_to="videos/thumbnails/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _extract_youtube_id(self, url):
        """Return YouTube video id or None for non-youtube urls."""
        if not url:
            return None
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        # youtu.be shortlinks: path = /VIDEOID
        if "youtu.be" in netloc:
            vid = parsed.path.lstrip("/").split("?")[0]
            return vid or None

        # youtube.com (watch?v=ID) or embed
        if "youtube.com" in netloc:
            # /watch?v=ID
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]
            # /embed/ID or /v/ID
            parts = parsed.path.split("/")
            for i, p in enumerate(parts):
                if p in ("embed", "v") and len(parts) > i + 1:
                    return parts[i + 1].split("?")[0]
        return None

    def save(self, *args, **kwargs):
        # ensure slug exists
        if not self.slug:
            self.slug = slugify(self.title)

        # Only try to auto-fetch thumbnail for YouTube links when thumbnail empty
        if not self.thumbnail and self.video_url:
            video_id = self._extract_youtube_id(self.video_url)
            if video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                try:
                    resp = urllib.request.urlopen(thumbnail_url)
                    if resp.getcode() == 200:
                        data = resp.read()
                        self.thumbnail.save(f"{video_id}.jpg", ContentFile(data), save=False)
                except Exception as e:
                    # keep it silent in production; print/log while debugging
                    print("Could not fetch YouTube thumbnail:", e)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def is_embedded(self):
        return bool(self.video_url)


class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Us")
    description = RichTextField(
        help_text="Rich text description for homepage and about page",
        default="This is our about description. Update in admin."
    )

    def __str__(self):
        return self.title


class FAQ(models.Model):
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "FAQs"

    def __str__(self):
        return f"{self.order}. {self.question}"


class WhyUsImage(models.Model):
    about_page = models.OneToOneField(AboutPage, on_delete=models.CASCADE, related_name="image")
    image = models.ImageField(upload_to="about/", blank=True, null=True)

    def __str__(self):
        return f"Image for {self.about_page.title}"



class Service(models.Model):
    number = models.PositiveIntegerField(help_text="Step number, e.g. 01, 02, 03")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    features = models.TextField(blank=True, help_text="Enter one feature per line")
    extra_details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}. {self.title}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.email

class PortfolioCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Portfolio Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Portfolio(models.Model):
    category = models.ForeignKey(PortfolioCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    client = models.CharField(max_length=255, blank=True, null=True)
    project_date = models.DateField()
    url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-project_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class PortfolioImage(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="portfolio/images/")
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.portfolio.title}"



class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
