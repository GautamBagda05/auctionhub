from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('art', 'Art & Collectibles'),
    ('fashion', 'Fashion & Accessories'),
    ('vehicles', 'Vehicles'),
    ('realestate', 'Real Estate'),
    ('jewelry', 'Jewelry & Watches'),
    ('sports', 'Sports & Outdoors'),
    ('other', 'Other'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('ended', 'Ended'),
    ('cancelled', 'Cancelled'),
]


class Auction(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='auction_images/', blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    reserve_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    current_bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_active(self):
        return self.status == 'active' and self.end_time > timezone.now()

    def time_remaining(self):
        if self.end_time > timezone.now():
            delta = self.end_time - timezone.now()
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours >= 24:
                days = hours // 24
                return f"{days}d {hours % 24}h"
            return f"{hours}h {minutes}m"
        return "Ended"

    def highest_bid(self):
        bid = self.bids.order_by('-amount').first()
        return bid.amount if bid else self.starting_bid

    def bid_count(self):
        return self.bids.count()

    def check_and_end(self):
        if self.end_time <= timezone.now() and self.status == 'active':
            self.status = 'ended'
            top_bid = self.bids.order_by('-amount').first()
            if top_bid:
                self.winner = top_bid.bidder
                self.current_bid = top_bid.amount
            self.save()


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        return f"{self.bidder.username} bid ₹{self.amount} on {self.auction.title}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='payment')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.auction.title} by {self.buyer.username}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='watchers')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'auction']

    def __str__(self):
        return f"{self.user.username} watching {self.auction.title}"

