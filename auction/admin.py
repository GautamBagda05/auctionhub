from django.contrib import admin
from .models import Auction, Bid, Payment, Watchlist

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display  = ['title', 'seller', 'category', 'starting_bid', 'current_bid', 'status', 'end_time']
    list_filter   = ['status', 'category']
    search_fields = ['title', 'seller__username']
    actions       = ['mark_ended']

    def mark_ended(self, request, queryset):
        queryset.update(status='ended')
    mark_ended.short_description = 'Mark selected auctions as ended'

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['auction', 'bidder', 'amount', 'placed_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['auction', 'buyer', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['auction__title', 'buyer__username']

    def get_queryset(self, request):
        return super().get_queryset(request)  # ✅ KEEP IT SIMPLE
    
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'auction', 'added_at']
