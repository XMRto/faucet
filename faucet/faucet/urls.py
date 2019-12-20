"""faucet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import status

from ratelimit.exceptions import Ratelimited

urlpatterns = [
    path("", include("transactions.urls")),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return JsonResponse(
            data={"error": ["Sorry you are blocked."]},
            status=status.HTTP_403_FORBIDDEN,
        )
