import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniCart.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from listings.models import Listing, Category

def populate():
    # 1. Create Users
    users_data = [
        ('alice', 'alice@example.com', 'AzraBora123'),
        ('bob', 'bob@example.com', 'AzraBora123'),
        ('charlie', 'charlie@example.com', 'AzraBora123'),
    ]
    
    users = []
    for username, email, password in users_data:
        user, created = User.objects.get_or_create(username=username, email=email)
        if created:
            user.set_password(password)
            user.save()
            UserProfile.objects.get_or_create(user=user, email_verified=True)
            print(f"Created user: {username}")
        users.append(user)

    # 2. Get Categories
    categories = list(Category.objects.all())
    if not categories:
        print("No categories found. Run add_categories.py first.")
        return

    # 3. Create Listings
    listings_data = [
        ('MacBook Pro M1', 'Great condition, 16GB RAM, 512GB SSD.', 25000, 'like_new'),
        ('Calculus Stewart 8th Edition', 'Used for one semester, minimal highlighting.', 450, 'good'),
        ('Dorm Desk Lamp', 'Adjustable brightness, LED.', 150, 'fair'),
        ('Nike Air Jordan 1', 'Size 42, worn once.', 3200, 'like_new'),
        ('Electric Guitar', 'Fender Squier, comes with amp.', 7500, 'good'),
    ]

    for title, desc, price, cond in listings_data:
        seller = random.choice(users)
        category = random.choice(categories)
        listing, created = Listing.objects.get_or_create(
            title=title,
            defaults={
                'seller': seller,
                'description': desc,
                'price': Decimal(price),
                'condition': cond,
                'category': category,
                'is_active': True,
                'is_sold': False
            }
        )
        if created:
            print(f"Created listing: {title} by {seller.username}")

    print("\nPopulation complete!")

if __name__ == '__main__':
    populate()
