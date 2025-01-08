from django.urls import path
from . import views
from .views import CreateUserView, SetLanguageView, TenantListView, TenantEditView, PersonsListView, PersonsDTView

urlpatterns = [
    path('person/register', CreateUserView.as_view(), name='person-register'),
    path('set-language/', SetLanguageView.as_view(), name='set-language'),
    path('persons/', PersonsListView.as_view(), name='persons'),
    path('person/<int:id>/edit', TenantEditView.as_view(), name='edit-person'),
    path('persons_dt', PersonsDTView.as_view(), name='persons_dt'),
    path('list_databases', views.list_dbs, name='list_dbs'),
    path('list_servers', views.list_servers, name='list_servers'),
]