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
    {'name': 'Technology & Electronics', 'icon': '💻', 'slug': 'technology-electronics'},
    {'name': 'Textbooks & Academics', 'icon': '📚', 'slug': 'textbooks-academics'},
    {'name': 'Living & Dorm Essentials', 'icon': '🛏️', 'slug': 'living-dorm-essentials'},
    {'name': 'Apparel & Accessories', 'icon': '👕', 'slug': 'apparel-accessories'},
    {'name': 'Hobbies & Sports', 'icon': '🎮', 'slug': 'hobbies-sports'},
    {'name': 'Tickets & Services', 'icon': '🎫', 'slug': 'tickets-services'},
]

for cat in categories:
    obj, created = Category.objects.update_or_create(
        slug=cat['slug'],
        defaults={'name': cat['name'], 'icon': cat['icon']}
    )
    status = 'Created' if created else 'Already exists'
    print(f"{status}: {obj.name}")

print(f"\nTotal categories: {Category.objects.count()}")
