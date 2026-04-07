from django.urls import path
from . import views

urlpatterns = [
    path('', views.auction_list, name='auction_list'),
    path('<int:pk>/', views.auction_detail, name='auction_detail'),
    path('<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('create/', views.create_auction, name='create_auction'),
    path('<int:pk>/edit/', views.edit_auction, name='edit_auction'),
    path('<int:pk>/watch/', views.toggle_watchlist, name='toggle_watchlist'),
    path('<int:pk>/pay/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('<int:pk>/updates/', views.get_bid_updates, name='bid_updates'),
    path('payment/success/', views.dummy_payment_success, name='dummy_payment_success'),
]
