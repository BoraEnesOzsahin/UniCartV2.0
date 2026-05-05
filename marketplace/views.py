from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, ProfileForm, ListingForm, ListingSearchForm
from .models import Listing, Category, Profile, University

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'marketplace/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    featured_listings = Listing.objects.all()[:6]  # Get first 6 listings
    categories = Category.objects.all()
    return render(request, 'marketplace/home.html', {
        'featured_listings': featured_listings,
        'categories': categories
    })

@login_required
def profile(request):
    # Ensure profile exists
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Get default university
        default_university = University.objects.first()
        if not default_university:
            default_university = University.objects.create(name="Default University", location="Default Location")
        profile = Profile.objects.create(user=request.user, university=default_university)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    user_listings = Listing.objects.filter(seller=request.user).order_by('-date')
    
    return render(request, 'marketplace/profile.html', {
        'form': form,
        'user_listings': user_listings
    })

def listing_list(request):
    listings = Listing.objects.all()
    form = ListingSearchForm(request.GET)
    
    if form.is_valid():
        # Check if category is selected and not empty
        if form.cleaned_data.get('category'):
            listings = listings.filter(categories=form.cleaned_data['category'])
        
        # Handle other filters
        if form.cleaned_data.get('min_price'):
            listings = listings.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price'):
            listings = listings.filter(price__lte=form.cleaned_data['max_price'])
        if form.cleaned_data.get('query'):
            listings = listings.filter(title__icontains=form.cleaned_data['query'])

    return render(request, 'marketplace/listing_list.html', {
        'listings': listings,
        'form': form,
        'selected_category': form.cleaned_data.get('category') if form.is_valid() else None
    })

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'marketplace/listing_detail.html', {'listing': listing})

@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            form.save_m2m()
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm()
    return render(request, 'marketplace/product_create.html', {'form': form})

@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'marketplace/product_create.html', {'form': form, 'editing': True})

@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if request.method == 'POST':
        listing.delete()
        return redirect('listing_list')
    return render(request, 'marketplace/product_delete.html', {'listing': listing})

def support(request):
    return render(request, 'marketplace/support.html')

def faq(request):
    return render(request, 'marketplace/faq.html')
