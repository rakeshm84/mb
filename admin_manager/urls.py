from django.urls import path
from .views import CreateUserView, SetLanguageView, TenantListView, TenantEditView, PersonsListView, PersonsDTView

urlpatterns = [
    path('person/register', CreateUserView.as_view(), name='person-register'),
    path('set-language/', SetLanguageView.as_view(), name='set-language'),
    path('persons/', PersonsListView.as_view(), name='persons'),
    path('person/<int:id>/edit', TenantEditView.as_view(), name='edit-person'),
    path('persons_dt', PersonsDTView.as_view(), name='persons_dt'),
]