from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from .models import Auction, Bid, Payment, Watchlist
from .forms import AuctionForm, BidForm
import razorpay
import json
import hmac
import hashlib


def auction_list(request):
    auctions = Auction.objects.filter(status='active').order_by('-created_at')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'newest')

    if category:
        auctions = auctions.filter(category=category)
    if search:
        auctions = auctions.filter(title__icontains=search)
    if min_price:
        auctions = auctions.filter(starting_bid__gte=min_price)
    if max_price:
        auctions = auctions.filter(starting_bid__lte=max_price)

    if sort == 'ending_soon':
        auctions = auctions.order_by('end_time')
    elif sort == 'most_bids':
        from django.db.models import Count
        auctions = auctions.annotate(bid_count=Count('bids')).order_by('-bid_count')
    elif sort == 'price_low':
        auctions = auctions.order_by('starting_bid')
    elif sort == 'price_high':
        auctions = auctions.order_by('-starting_bid')

    from .models import CATEGORY_CHOICES
    return render(request, 'auction/auction_list.html', {
        'auctions': auctions,
        'categories': CATEGORY_CHOICES,
        'selected_category': category,
        'search': search,
        'sort': sort,
    })


def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    auction.check_and_end()
    auction.views_count += 1
    auction.save(update_fields=['views_count'])

    bids = auction.bids.order_by('-amount')[:10]
    bid_form = BidForm(auction=auction)
    is_watching = False
    user_highest_bid = None

    if request.user.is_authenticated:
        is_watching = Watchlist.objects.filter(user=request.user, auction=auction).exists()
        user_highest_bid = auction.bids.filter(bidder=request.user).order_by('-amount').first()

    return render(request, 'auction/auction_detail.html', {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
        'is_watching': is_watching,
        'user_highest_bid': user_highest_bid,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    })


@login_required
def place_bid(request, pk):
    if request.method != 'POST':
        return redirect('auction_detail', pk=pk)

    auction = get_object_or_404(Auction, pk=pk)

    # Check auction active
    if not auction.is_active():
        messages.error(request, 'This auction has ended.')
        return redirect('auction_detail', pk=pk)

    # Prevent self bidding
    if auction.seller == request.user:
        messages.error(request, 'You cannot bid on your own auction.')
        return redirect('auction_detail', pk=pk)

    form = BidForm(request.POST, auction=auction)

    if form.is_valid():
        bid = form.save(commit=False)
        bid.auction = auction
        bid.bidder = request.user
        bid.save()

        # Update auction price
        auction.current_bid = bid.amount
        auction.save()

        messages.success(request, f'Your bid of ₹{bid.amount} placed successfully!')
    else:
        for error in form.errors.values():
            messages.error(request, error[0])

    return redirect('auction_detail', pk=pk)

@login_required
def create_auction(request):
    profile = request.user.profile
    if profile.role not in ['seller', 'admin'] and not request.user.is_staff:
        messages.error(request, 'Only sellers can create auctions.')
        return redirect('home')

    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.status = 'active'
            auction.save()
            messages.success(request, 'Auction created successfully!')
            return redirect('auction_detail', pk=auction.pk)
    else:
        form = AuctionForm()

    return render(request, 'auction/create_auction.html', {'form': form})


@login_required
def edit_auction(request, pk):
    auction = get_object_or_404(Auction, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES, instance=auction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auction updated!')
            return redirect('auction_detail', pk=auction.pk)
    else:
        form = AuctionForm(instance=auction)
    return render(request, 'auction/create_auction.html', {'form': form, 'auction': auction})


@login_required
def toggle_watchlist(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    obj, created = Watchlist.objects.get_or_create(user=request.user, auction=auction)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


@login_required
def payment_view(request, pk):
    auction = get_object_or_404(Auction, pk=pk)

    if auction.winner != request.user:
        messages.error(request, 'You are not the winner of this auction.')
        return redirect('auction_detail', pk=pk)

    if request.method == "POST":
        # ✅ Dummy payment success
        payment, created = Payment.objects.get_or_create(
            auction=auction,
            buyer=request.user,
            defaults={'amount': auction.current_bid}
        )

        payment.status = 'completed'
        payment.save()

        messages.success(request, '✅ Payment successful (Dummy)! Seller notified.')
        return redirect('auction_detail', pk=pk)

    return render(request, 'auction/dummy_payment.html', {
        'auction': auction
    })


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = request.POST
        try:
            razorpay_order_id = data['razorpay_order_id']
            razorpay_payment_id = data['razorpay_payment_id']
            razorpay_signature = data['razorpay_signature']

            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }
            client.utility.verify_payment_signature(params)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'completed'
            payment.save()
            messages.success(request, 'Payment successful! The seller will be notified.')
            return redirect('auction_detail', pk=payment.auction.pk)
        except Exception as e:
            messages.error(request, 'Payment verification failed.')
            return redirect('home')
    return redirect('home')


def get_bid_updates(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    auction.check_and_end()
    bids = list(
        auction.bids.order_by('-amount')
        .values('bidder__username', 'amount', 'placed_at')[:5]
    )
    for b in bids:
        b['placed_at'] = b['placed_at'].strftime('%H:%M:%S')
        b['amount'] = str(b['amount'])
    return JsonResponse({
        'current_bid': str(auction.highest_bid()),
        'bid_count': auction.bid_count(),
        'status': auction.status,
        'time_remaining': auction.time_remaining(),
        'bids': bids,
    })
from .models import Payment, Auction

def dummy_payment_success(request):
    if request.method == "POST":
        ref = request.POST.get("ref")

        auction = Auction.objects.get(reference=ref)

        payment, created = Payment.objects.get_or_create(
            auction=auction,
            defaults={
                'buyer': request.user,
                'amount': auction.current_bid,
                'status': 'completed'
            }
        )

        if not created:
            payment.status = 'completed'
            payment.save()

        return redirect('auction_detail', pk=auction.pk)