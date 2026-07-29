from django.urls import path

from .google_auth import google_login_user
from .views import (
    
    get_sites,
    get_site_details, 
    create_site_with_details,
    edit_site_with_details,
    delete_site_with_details,

    get_contractors,
    create_contractor,
    delete_contractor,
    edit_contractor,

    create_equipment,
    delete_equipment,
    get_sites_by_amc_status,

)
from .users import (

    login_user,
    
    create_user,
    delete_user,
    edit_user,
    list_users,
    )

urlpatterns = [
    #Google auth (sso)
    path('auth/google/', google_login_user, name='google_login_user'),

    #Site APIs
    path('sites/', get_sites, name='get_sites'),
    path('site-details/<int:site_id>/', get_site_details, name='get_site_details'),
    path('create-site/', create_site_with_details, name='create_site_with_details'),
    path('edit-site/<int:site_id>/', edit_site_with_details, name='edit_site_with_details'),
    path('delete-site/<int:site_id>/', delete_site_with_details, name='delete_site_with_details'),
    path('sites/amc-status/', get_sites_by_amc_status, name='get_sites_by_amc_status'),
    
    #Contractor APIs
    path('contractors/', get_contractors, name='get_contractors'),
    path('create-contractor/', create_contractor, name='create_contractor'),
    path('delete-contractor/<int:contractor_id>/', delete_contractor, name='delete_contractor'),
    path('edit-contractor/<int:contractor_id>/', edit_contractor, name='edit_contractor'),
    #Equipment APIs
    path('create-equipment/', create_equipment, name='create_equipment'),
    path('delete-equipment/<int:equipment_id>/', delete_equipment, name='delete_equipment'),

    #User APIs
    path('auth/login/', login_user, name='login_user'),
    path('create-user/', create_user, name='create_user'),
    path('users/', list_users, name='list_users'),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
]