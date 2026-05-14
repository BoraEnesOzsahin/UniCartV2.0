from django.db import models
from django.contrib.auth.models import User

# ─────────────────────────────────────────
#  CATEGORY
#  Stores item categories (Electronics, Books, etc.)
#  Admin adds these through the admin panel
# ─────────────────────────────────────────
class Category(models.Model):
    name  = models.CharField(max_length=100)
    icon  = models.CharField(max_length=10, blank=True)   # emoji icon e.g. "💻"
    slug  = models.SlugField(unique=True)                  # used in URLs: /category/electronics/

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# ─────────────────────────────────────────
#  LISTING
#  One item posted for sale by a student
# ─────────────────────────────────────────
class Listing(models.Model):

    CONDITION_CHOICES = [
        ('like_new', 'Like New'),
        ('good',     'Good'),
        ('fair',     'Fair'),
    ]

    # Who posted it — when user is deleted, their listings are too
    seller    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')

    # Basic info
    title       = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    condition   = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    image       = models.ImageField(upload_to='listings/', blank=True, null=True)

    # Category link
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='listings')

    # Status
    is_sold    = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=True)

    # Timestamps — set automatically
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']   # newest first


# ─────────────────────────────────────────
#  FAVORITE  (ManyToMany bonus feature)
#  A user can save listings to their favorites
# ─────────────────────────────────────────
class Favorite(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')   # can't favorite the same item twice

    def __str__(self):
        return f"{self.user.username} → {self.listing.title}"
