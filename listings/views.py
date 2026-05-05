from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Listing, Category
from .forms import ListingForm


# ─────────────────────────────────────────
#  HOME PAGE
#  Shows featured/recent listings
#  URL: /
# ─────────────────────────────────────────
def home(request):
    listings   = Listing.objects.filter(is_active=True, is_sold=False)[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'listings':   listings,
        'categories': categories,
    })


# ─────────────────────────────────────────
#  LISTING LIST  (Browse all)
#  Supports search + category filter + pagination
#  URL: /listings/
# ─────────────────────────────────────────
def listing_list(request):
    listings = Listing.objects.filter(is_active=True, is_sold=False)

    # --- Search ---
    query = request.GET.get('q')
    if query:
        listings = listings.filter(title__icontains=query)

    # --- Category filter ---
    category_slug = request.GET.get('category')
    if category_slug:
        listings = listings.filter(category__slug=category_slug)

    # --- Pagination (8 per page) ---
    paginator = Paginator(listings, 8)
    page      = request.GET.get('page')
    listings  = paginator.get_page(page)

    categories = Category.objects.all()
    return render(request, 'listings/list.html', {
        'listings':   listings,
        'categories': categories,
        'query':      query,
    })


# ─────────────────────────────────────────
#  LISTING DETAIL
#  Shows one listing in full
#  URL: /listings/<id>/
# ─────────────────────────────────────────
def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    return render(request, 'listings/detail.html', {'listing': listing})


# ─────────────────────────────────────────
#  CREATE LISTING
#  Only logged-in users can post
#  URL: /listings/create/
# ─────────────────────────────────────────
@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user      # attach current user as seller
            listing.save()
            messages.success(request, 'Your listing is live!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm()

    return render(request, 'listings/create.html', {'form': form})


# ─────────────────────────────────────────
#  EDIT LISTING
#  Only the seller can edit their own listing
#  URL: /listings/<id>/edit/
# ─────────────────────────────────────────
@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)

    return render(request, 'listings/edit.html', {'form': form, 'listing': listing})


# ─────────────────────────────────────────
#  DELETE LISTING
#  Only the seller can delete their own listing
#  URL: /listings/<id>/delete/
# ─────────────────────────────────────────
@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)

    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('listing_list')

    return render(request, 'listings/delete.html', {'listing': listing})
