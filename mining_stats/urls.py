"""
Definition of urls for MiningStats.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

from django.conf.urls import include
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r"^$", app.views.stats, name="stats"),
    url(r"^restart/(\d+)/$", app.views.restart, name="restart"),
    url(r"^reboot/(\d+)/$", app.views.reboot, name="reboot"),
    url(
        r"^charts/(?P<rig_id>\d+)/(?:(?P<hours>\d+)/)?$", app.views.chart, name="charts"
    ),
    url(
        r"^login/$",
        django.contrib.auth.views.login,
        {
            "template_name": "app/login.html",
            "authentication_form": app.forms.BootstrapAuthenticationForm,
            "extra_context": {"title": "Log in"},
        },
        name="login",
    ),
    url(
        r"^logout$", django.contrib.auth.views.logout, {"next_page": "/"}, name="logout"
    ),
    url(r"^admin/", include(admin.site.urls)),
]
