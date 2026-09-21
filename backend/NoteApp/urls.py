"""
URL configuration for NoteApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from django.urls import include
from django.http import JsonResponse


def assetlinks(request):
    return JsonResponse([
        {
            "relation": [
                "delegate_permission/common.handle_all_urls"
            ],
            "target": {
                "namespace": "android_app",
                "package_name": "com.anonymous.SmartNotesMobile",
                "sha256_cert_fingerprints": [
                    "FA:C6:17:45:DC:09:03:78:6F:B9:ED:E6:2A:96:2B:39:9F:73:48:F0:BB:6F:89:9B:83:32:66:75:91:03:3B:9C"
                ]
            }
        }
    ], safe=False)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("NoteAppApi.urls")),
    path("api/auth/", include("NoteAppCore.urls")),
    path(
        ".well-known/assetlinks.json",
        assetlinks,
        name="assetlinks"
    ),
]
