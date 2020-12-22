from django.urls import path
from . import views

app_name = 'phaster'
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('siteusage', views.UsageView.as_view(), name='siteusage'),
    # path('pagenotfound', views.PageNotFoundView.as_view(), name='pagenotfound'),
    path('<str:keyword>/results', views.results, name='results'),
    # path('<str:keyword>/results/<str:asin>/submittedanalysis/', views.submitted_analysis, name='submittedanalysis'),
    # path('<str:keyword>/results/<str:asin>', views.analysis, name='analysis'),
]