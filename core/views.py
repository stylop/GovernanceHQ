from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Event, Blog, Category, Publication, PhotoCategory, Photo, VideoCategory, Video, AboutPage, Service, \
    PublicationCategory, NewsletterSubscriber, PortfolioCategory, Portfolio
from datetime import date
from django.contrib import messages
from .forms import NewsletterForm, ContactForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.


def home(request):
    latest_blogs = Blog.objects.all().order_by("-created_at")[:3]
    today = date.today()
    events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')[:3]
    categories = PhotoCategory.objects.all()
    photos = Photo.objects.all()[:9]  # limit to 9 latest photos for homepage
    latest_videos = Video.objects.all().order_by("-id")[:3]  # show 3 latest videos
    about = AboutPage.objects.first()
    services = Service.objects.all()[:3]  # Only 3 services for homepage
    latest_publications = Publication.objects.all().order_by("-created_at")[:3]  # show last 3
    # Add newsletter form
    newsletter_form = NewsletterForm()
    form = ContactForm()
    return render(request, "core/home.html", {
        "events": events ,
        "latest_blogs": latest_blogs,
        "categories": categories,
        "photos": photos,
        "latest_videos": latest_videos,
        "about": about,
        "services": services,
        "latest_publications": latest_publications,
        "form": form,
        "newsletter_form": newsletter_form,

    })


def about_page(request):
    about = AboutPage.objects.first()
    return render(request, "core/about.html", {"about": about})


def past_events(request):
    today = timezone.now().date()
    events = Event.objects.filter(date__lt=today).order_by("-date")
    paginator = Paginator(events, 6)  # show 6 events per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "core/events.html", {"page_obj": page_obj,
        "events": page_obj,})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    blog = category.blogs.all()  # uses related_name="blogs"
    paginator = Paginator(blog, 6)  # 6 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "core/category_posts.html", {
        "category": category,
        "blog": blog,
        "page_obj": page_obj,
    })


def services_page(request):
    services = Service.objects.all()
    return render(request, "core/services.html", {"services": services})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    services = Service.objects.all().order_by("number")
    return render(request, "core/service_detail.html", {
        "service": service,
        "services": services
    })


def membership(request):
    return render(request, 'core/membership.html')

def programs(request):
    return render(request, 'core/programs.html')

def resources(request):
    return render(request, 'core/resources.html')

def blog_list(request, slug=None):
    query = request.GET.get("q", "")
    posts = Blog.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    paginator = Paginator(posts, 6)  # 6 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    category_obj = None
    if slug:  # Category filter
        category_obj = get_object_or_404(Category, slug=slug)
        posts = posts.filter(category=category_obj)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Keep your recent posts + categories as before
    recent_posts = Blog.objects.all().order_by('-created_at')[:5]
    categories = Category.objects.all()

    return render(
        request,
        "core/blog_list.html",
        {
            "page_obj": page_obj,
            "recent_posts": recent_posts,
            "categories": categories,
            "query": query,  # send back search term
            "selected_category": category_obj,
        },
    )
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    recent_posts = Blog.objects.all().order_by('-created_at')[:5]  # last 5
    categories = Category.objects.all()
    return render(request, "core/blog_detail.html", {"blog": blog, "recent_posts": recent_posts, "categories": categories})

def publications_list(request):
    publications = Publication.objects.all().order_by("-created_at")
    query = request.GET.get("q")
    category_slug = request.GET.get("category")
    paginator = Paginator(publications, 6)  # 6 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categories = PublicationCategory.objects.all()

    # Search
    if query:
        publications = publications.filter(title__icontains=query)

    # Category filter
    if category_slug:
        category = get_object_or_404(PublicationCategory, slug=category_slug)
        publications = publications.filter(category=category)
    else:
        category = None

    return render(request, "core/publications_list.html", {"publications": publications,"categories": categories,"page_obj": page_obj,"query": query,
        "active_category": category,})

def publication_detail(request, slug):
    publication = get_object_or_404(Publication, slug=slug)
    category_slug = request.GET.get("category")
    categories = PublicationCategory.objects.all()

    # Category filter
    if category_slug:
        category = get_object_or_404(PublicationCategory, slug=category_slug)
        publication = publication.filter(category=category)
    else:
        category = None
    return render(request, "core/publication_detail.html", {"publication": publication, "categories": categories})

def publication_category(request, slug):
    category = get_object_or_404(PublicationCategory, slug=slug)
    publications = Publication.objects.filter(category=category).order_by('-id')

    paginator = Paginator(publications, 6)  # show 6 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "core/publications_list.html", {
        "page_obj": page_obj,
        "categories": PublicationCategory.objects.all(),
        "selected_category": category,
    })

def photo_gallery(request):
    categories = PhotoCategory.objects.all()
    photos = Photo.objects.all()
    return render(request, "core/photo_gallery.html", {
        "categories": categories,
        "photos": photos,
    })

def photo_category(request, slug):
    category = get_object_or_404(PhotoCategory, slug=slug)
    photos = category.photos.all()
    return render(request, "core/photo_gallery.html", {
        "categories": PhotoCategory.objects.all(),
        "photos": photos,
        "active_category": category,
    })


def videos_list(request):
    categories = VideoCategory.objects.all()
    videos = Video.objects.all().order_by("-id")  # optional: newest first

    paginator = Paginator(videos, 6)  # show 6 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/videos_list.html", {
        "categories": categories,
        "videos": page_obj,   # ✅ videos loop
        "page_obj": page_obj, # ✅ pagination controls
    })

def video_category(request, slug):
    category = get_object_or_404(VideoCategory, slug=slug)
    videos = category.videos.all()
    categories = VideoCategory.objects.all()
    return render(request, "core/videos_list.html", {"categories": categories, "videos": videos, "current_category": category})


def subscribe_newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()

            # AJAX request → return JSON
            if request.headers.get("x-requested-with", "").lower() == "xmlhttprequest":
                return JsonResponse({
                    "status": "success",
                    "message": "You have successfully subscribed!"
                })

            # Normal form → fallback redirect
            return redirect(request.META.get("HTTP_REFERER", "/"))

        else:
            # AJAX request → return JSON
            if request.headers.get("x-requested-with", "").lower() == "xmlhttprequest":
                return JsonResponse({
                    "status": "error",
                    "message": "This email is already subscribed or invalid."
                })

            # Normal form → fallback redirect
            return redirect(request.META.get("HTTP_REFERER", "/"))

    # GET or other → just redirect home
    return redirect("/")



def unsubscribe_newsletter(request, token):
    subscriber = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
    if request.method == "POST":
        subscriber.delete()
        return render(request, "newsletter/unsubscribed.html")
    return render(request, "newsletter/confirm_unsubscribe.html", {"subscriber": subscriber})

def portfolio_list(request):
    portfolios = Portfolio.objects.all().order_by("-id")   # newest first
    categories = PortfolioCategory.objects.all()

    paginator = Paginator(portfolios, 9)  # show 9 portfolios per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/portfolio.html", {
        "page_obj": page_obj,
        "portfolios": page_obj,   # so template loop still works
        "categories": categories,
    })

def portfolio_detail(request, slug):
    portfolio = get_object_or_404(Portfolio, slug=slug)
    return render(request, "core/portfolio_detail.html", {"portfolio": portfolio})


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Handle AJAX request
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "success",
                    "message": "Your message has been sent. Thank you!"
                })
            # Normal fallback (non-AJAX)
            messages.success(request, "Your message has been sent. Thank you!")
            return redirect(request.path)
        else:
            # Collect errors as dict
            errors = {field: list(error_list) for field, error_list in form.errors.items()}

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "error",
                    "errors": errors
                })
            messages.error(request, "There was an error. Please check the form.")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})
