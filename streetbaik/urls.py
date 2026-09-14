from django.contrib import admin
from django.urls import path
from cafe import views
urlpatterns=[
 path("admin/",admin.site.urls), path("",views.home,name="home"), path("account/login/",views.customer_login,name="customer_login"), path("account/register/",views.customer_register,name="customer_register"), path("account/logout/",views.customer_logout,name="customer_logout"), path("track/",views.track,name="track"), path("staff/",views.staff_login,name="staff"), path("staff/logout/",views.staff_logout,name="staff_logout"),
 path("api/menu/",views.api_menu,name="api_menu"), path("api/orders/",views.create_order,name="create_order"), path("api/orders/<str:public_id>/",views.get_order,name="get_order"), path("api/reservations/",views.create_reservation,name="create_reservation"), path("api/reviews/",views.create_review,name="create_review"), path("api/messages/",views.create_message,name="create_message"),
 path("staff/orders/<int:order_id>/status/",views.update_order_status,name="update_order_status"), path("staff/reservations/<int:item_id>/status/",views.update_reservation_status,name="update_reservation_status"), path("staff/reviews/<int:item_id>/status/",views.update_review_status,name="update_review_status"),
]
