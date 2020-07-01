from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from . import views

urlpatterns = [
    path("", views.HomeView, name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    path(
        "tutorial/", TemplateView.as_view(template_name="pages/tutorial.html"), name="tutorial"
    ),
    path(
        "statistics/", TemplateView.as_view(template_name="pages/statistics.html"), name="statistics"
    ),
    path(
        "help/", TemplateView.as_view(template_name="pages/help.html"), name="help"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("groups/", include("geneulike.groups.urls", namespace="groups")),
    path("users/", include("geneulike.users.urls", namespace="users")),
    path("jobs/", include("geneulike.jobs.urls", namespace="jobs")),
    path("genes/", include("geneulike.genes.urls", namespace="genes")),
    path("studies/", include("geneulike.studies.urls", namespace="studies")),
    path("series/", include("geneulike.series.urls", namespace="series")),
    path("genelists/", include("geneulike.genelists.urls", namespace="genelists")),
    path("species/", include("geneulike.species.urls", namespace="species")),
    path("platforms/", include("geneulike.platforms.urls", namespace="platforms")),
    path("accounts/", include("allauth.urls")),
    path("ontologies/", include("geneulike.ontologies.urls", namespace="ontologies")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
