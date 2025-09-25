from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name = 'home'),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path('services/', views.services_page, name='services'),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path('membership/', views.membership, name='membership'),
    path('programs/', views.programs, name='programs'),
    path('resources/', views.resources, name='resources'),
    path("blogs/", views.blog_list, name="blog_list"),
    path("blog/category/<slug:slug>/", views.blog_list, name="blog_by_category"),
    path("blogs/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path('events/', views.past_events, name='past_events'),
    path("category/<slug:slug>/", views.category_posts, name="category_posts"),
    path("publications/", views.publications_list, name="publications_list"),
    path("publications/<slug:slug>/", views.publication_detail, name="publication_detail"),
    path("publications/category/<slug:slug>/", views.publication_category, name="publication_category"),
    path("gallery/", views.photo_gallery, name="photo_gallery"),
    path("gallery/<slug:slug>/", views.photo_category, name="photo_category"),
    path("videos/", views.videos_list, name="videos_list"),
    path("videos/<slug:slug>/", views.video_category, name="video_category"),
    path("subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),
    path("newsletter/unsubscribe/<uuid:token>/", views.unsubscribe_newsletter, name="unsubscribe_newsletter"),
    path("portfolio/", views.portfolio_list, name="portfolio"),
    path("portfolio/<slug:slug>/", views.portfolio_detail, name="portfolio_detail"),



]