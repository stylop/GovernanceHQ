from .models import Service

def footer_services(request):
    return {
        "footer_services": Service.objects.all().order_by("title")[:4]  # you can limit if needed
    }
