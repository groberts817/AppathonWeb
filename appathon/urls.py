from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'appathon.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^device/register/(?P<device_type>\w+)/$', 'appathon.views.register_device', name='register_device'),
)

if 'idea' in settings.INSTALLED_APPS and 'django.contrib.comments' in settings.INSTALLED_APPS and 'haystack' in settings.INSTALLED_APPS:
        urlpatterns.append(url(r'^haystack/', include('haystack.urls')))
        urlpatterns.append(url(r'^comments/', include('django.contrib.comments.urls')))
        urlpatterns.append(url(r'^idea/', include('idea.urls', namespace="idea")))
        urlpatterns.append(url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}))
