from django.db import migrations


def create_default_categories(apps, schema_editor):
    Category = apps.get_model('listings', 'Category')
    categories = [
        {'name': 'Technology & Electronics', 'icon': '💻', 'slug': 'technology-electronics'},
        {'name': 'Textbooks & Academics', 'icon': '📚', 'slug': 'textbooks-academics'},
        {'name': 'Living & Dorm Essentials', 'icon': '🛏️', 'slug': 'living-dorm-essentials'},
        {'name': 'Apparel & Accessories', 'icon': '👕', 'slug': 'apparel-accessories'},
        {'name': 'Hobbies & Sports', 'icon': '🎮', 'slug': 'hobbies-sports'},
        {'name': 'Tickets & Services', 'icon': '🎫', 'slug': 'tickets-services'},
    ]

    for cat in categories:
        Category.objects.update_or_create(
            slug=cat['slug'],
            defaults={'name': cat['name'], 'icon': cat['icon']}
        )


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('listings', 'Category')
    slugs = [
        'technology-electronics',
        'textbooks-academics',
        'living-dorm-essentials',
        'apparel-accessories',
        'hobbies-sports',
        'tickets-services',
    ]
    Category.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
