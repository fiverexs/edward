from .models import WebsiteConfiguration

def website_configuration(request):
    config = WebsiteConfiguration.objects.first()
    return {'config': config}