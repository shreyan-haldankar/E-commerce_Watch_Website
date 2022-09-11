from unicodedata import category
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
# from django.urls import reverse
from django_countries.fields import CountryField
import uuid


CATEGORY_CHOICES = (
    ('A', 'Analog'),
    ('C', 'Chronograph'),
    ('S', 'SmartWatch')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

# Create your models here.


class Item(models.Model):
    # id = models.UUIDField(default=uuid.uuid4, unique=True,
    #                       primary_key=True, editable=False)
    title = models.CharField(max_length=50)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES, default=("A", 'Analog'), max_length=1)
    label = models.CharField(choices=LABEL_CHOICES,
                             default=("P", 'primary'), max_length=1)
    slug = models.SlugField()
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={'slug': self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    ordered = models.BooleanField(default=False)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    apartment_address = models.CharField(max_length=200, null=True, blank=True)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username
