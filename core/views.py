from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from re import template
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView, TemplateView, View
from django.utils import timezone
# Create your views here.

# def item_list(request):
#     items = Item.objects.all()
#     context = {
#         "items": items
#     }
#     # return render(request, 'item_list.html', context)
#     return render(request, "home-page.html", context)


def checkout(request):
    context = {}
    return render(request, "checkout-page.html", context)

# def productItem(request):
#     context = {}
#     return render(request, "product-page.html", context)


class ProductsView(ListView):
    model = Item
    paginate_by = 10
    template_name = "products.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            context = {'object': order}
            return render(self.request, 'order_summary.html',context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('/products')
    

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered = False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # If order item is in order
        if order.items.filter(item__slug = item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "The item quantity was updated")
            return redirect('product', slug=slug)

        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
            return redirect('product', slug=slug)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user,ordered_date= ordered_date)

        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect('product', slug=slug)





# Remove from the cart
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # If order item is in order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered = False)[0]

            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
            return redirect('product', slug=slug)

        else:
            # Add a message saying that the order doesn't exist
            messages.info(request, "This item was not in your cart")

            return redirect('product', slug=slug)
            
            
    else:
        # add a message that the user doesn't have an order

        messages.info(request, "You do not have an active order")
        return redirect('product',slug = slug)
    