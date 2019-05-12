from django.urls import path
from . import views

app_name='ob'
urlpatterns=[
    path('',views.ob_index,name="index"),
    path('login/',views.ob_login,name="login"),
    path('logout/',views.ob_logout,name='logout'),
    path('register/',views.ob_register,name="register"),
    path('purchasing_record/',views.purchasing_record,name="puchasing_record"),
    path('add_shopping_cart/',views.add_shopping_cart,name="add_shopping_cart"),
    path('settle_accounts/',views.settle_accounts,name='settle_accounts'),
    path('show_shopping_cart/',views.show_shopping_cart,name="show_shopping_cart"),
    path('update_cart/',views.update_cart,name='update_cart'),
    path('show_shopping_records/',views.show_shopping_records,name="show_shopping_records"),
    path('search_books/',views.search_books,name='search_books'),
    path("buy_book/",views.buy_book,name='buy_book'),
    path("get_book/",views.get_book,name='get_book')

]
