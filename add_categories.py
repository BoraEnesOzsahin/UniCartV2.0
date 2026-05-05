#!/usr/bin/env python
"""
Script to populate categories in the database.
Run with: python manage.py shell < add_categories.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniCart.settings')
django.setup()

from listings.models import Category
from django.utils.text import slugify

categories = [
    {'name': 'Technology & Electronics', 'icon': '💻'},
    {'name': 'Textbooks & Academics', 'icon': '📚'},
    {'name': 'Living & Dorm Essentials', 'icon': '🛏️'},
    {'name': 'Apparel & Accessories', 'icon': '👕'},
    {'name': 'Hobbies & Sports', 'icon': '🎮'},
    {'name': 'Tickets & Services', 'icon': '🎫'},
]

for cat in categories:
    obj, created = Category.objects.get_or_create(
        name=cat['name'],
        defaults={'slug': slugify(cat['name']), 'icon': cat['icon']}
    )
    status = 'Created' if created else 'Already exists'
    print(f"{status}: {obj.name}")

print(f"\nTotal categories: {Category.objects.count()}")
