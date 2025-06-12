from django.utils.deprecation import MiddlewareMixin
from .models import PageView

class PageViewCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip admin and AJAX
        if not request.path.startswith('/admin/') and request.headers.get('x-requested-with') != 'XMLHttpRequest':
            pv, created = PageView.objects.get_or_create(pk=1)
            pv.count += 1
            pv.save()
