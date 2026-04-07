from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm, ProfileUpdateForm
from .models import UserProfile
from auction.models import Auction, Bid
from django.views.decorators.csrf import csrf_exempt

def get_or_create_profile(user):
    """
    Always-safe helper — returns the profile, creating it if missing.
    Handles superusers created via createsuperuser (no signup form).
    """
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'admin' if user.is_staff else 'buyer'}
    )
    return profile


def home(request):
    featured    = Auction.objects.filter(status='active').order_by('-created_at')[:6]
    ending_soon = Auction.objects.filter(status='active').order_by('end_time')[:4]
    total_auctions = Auction.objects.filter(status='active').count()
    total_users    = UserProfile.objects.count()
    return render(request, 'core/home.html', {
        'featured':       featured,
        'ending_soon':    ending_soon,
        'total_auctions': total_auctions,
        'total_users':    total_users,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            role = request.POST.get('role', 'buyer')
            if role not in ['buyer', 'seller']:
                role = 'buyer'

            user = form.save()

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role':  role,
                    'phone': form.cleaned_data.get('phone', ''),
                }
            )
            if not created:
                profile.role  = role
                profile.phone = form.cleaned_data.get('phone', '')
                profile.save()

            login(request, user)
            messages.success(request, f'Welcome to AuctionHub, {user.first_name or user.username}!')
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Ensure profile exists for every user on login (safety net)
            get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Use the safe helper — never crashes even for superusers
    profile = get_or_create_profile(request.user)

    if request.user.is_staff or profile.role == 'admin':
        from django.contrib.auth.models import User as AuthUser
        all_auctions = Auction.objects.all().order_by('-created_at')
        all_users    = AuthUser.objects.all()
        return render(request, 'profile/admin/dashboard.html', {
            'all_auctions': all_auctions,
            'all_users':    all_users,
        })

    elif profile.role == 'seller':
        my_auctions  = Auction.objects.filter(seller=request.user).order_by('-created_at')
        total_bids   = Bid.objects.filter(auction__seller=request.user).count()
        active_count = my_auctions.filter(status='active').count()
        return render(request, 'profile/seller/dashboard.html', {
            'my_auctions':  my_auctions,
            'total_bids':   total_bids,
            'active_count': active_count,
        })

    else:  # buyer (default)
        my_bids = Bid.objects.filter(bidder=request.user).order_by('-placed_at')
        won     = Auction.objects.filter(winner=request.user)
        return render(request, 'profile/buyer/dashboard.html', {
            'my_bids': my_bids,
            'won':     won,
        })


@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile/profile.html', {'form': form, 'profile': profile})

@csrf_exempt
def dummy_payment_success(request):
    if request.method == "POST":
        ref = request.POST.get("ref")
        method = request.POST.get("method")

        return render(request, "core/payment_success.html", {
            "ref": ref,
            "method": method
        })

    return redirect("home")