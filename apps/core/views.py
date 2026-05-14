from django.shortcuts import render

def home(request):
    # This might be redundant if we use listings.views.home
    # But we can keep it for future general home page changes
    from listings.models import Listing, Category
    listings = Listing.objects.filter(is_active=True, is_sold=False)[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'listings': listings,
        'categories': categories,
    })

def support(request):
    return render(request, 'marketplace/support.html')

def faq(request):
    return render(request, 'marketplace/faq.html')
