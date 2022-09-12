from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from re import template
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Order, OrderItem, BillingAddress
from django.views.generic import ListView, DetailView, TemplateView, View
from django.utils import timezone
from .forms import CheckoutForm
# Create your views here.

# def item_list(request):
#     items = Item.objects.all()
#     context = {
#         "items": items
#     }
#     # return render(request, 'item_list.html', context)
#     return render(request, "home-page.html", context)


class CheckoutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()

        context = {'form': form}
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        # print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
            # print("Form is Valid")
            # print(form.cleaned_data)
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # Add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'save_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user, street_address=street_address, apartment_address=apartment_address, country=country, zip=zip)
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # Todo add a redirect to select the payment option
                return redirect('checkout')
            messages.warning(self.request, "Failed Checkout")
            return redirect('checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('order-summary')
        

# def productItem(request):
#     context = {}
#     return render(request, "product-page.html", context)
def HomeView(request):
    return render(request,'home.html')


class ProductsView(ListView):
    model = Item
    paginate_by = 10
    template_name = "products.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object': order}
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('/products')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # If order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "The item quantity was updated")
            return redirect('order-summary')

        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
            return redirect('order-summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)

        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect('order-summary')


# Remove from the cart
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # If order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]

            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart")
            return redirect('order-summary')

        else:
            # Add a message saying that the order doesn't exist
            messages.info(request, "This item was not in your cart")

            return redirect('product', slug=slug)

    else:
        # add a message that the user doesn't have an order

        messages.info(request, "You do not have an active order")
        return redirect('product', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # If order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()

            # order.items.remove(order_item)
            messages.info(request, "The item quantity was updated.")
            return redirect('order-summary')

        else:
            # Add a message saying that the order doesn't exist
            messages.info(request, "This item was not in your cart")

            return redirect('product', slug=slug)

    else:
        # add a message that the user doesn't have an order

        messages.info(request, "You do not have an active order")
        return redirect('product', slug=slug)
