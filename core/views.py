from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from re import template
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Order, OrderItem, BillingAddress, Payment
from django.views.generic import ListView, DetailView, TemplateView, View
from django.utils import timezone
from .forms import CheckoutForm
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
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
                if payment_option == "S":
                    return redirect('payment', payment_option='stripe')
                elif payment_option == "P":

                    return redirect('payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid Payment option selected ")
                    return redirect('checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('order-summary')
        

class PaymentView(View):
    def get(self, *args, **kwargs):
        #order
        order = Order.objects.get(user = self.request.user, ordered = False)
        context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
            }
        return render(self.request, 'payment.html', context)
    def post(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        amount=int(order.get_total()*100)
        token = self.request.POST.get('stripeToken')
        
        
        try:
  # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=token,
            )

            #  create the payment
            payment  = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "Your order was successful!")
            return redirect("/")
            
        except stripe.error.CardError as e:
# Since it's a decline, stripe.error.CardError will be caught

            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:    
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

            
        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")


            # Invalid parameters were supplied to Stripe's API
            
        except stripe.error.AuthenticationError as e:
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

# Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            pass
        except stripe.error.APIConnectionError as e:
            messages.warning(self.request, "Network error")
            return redirect("/")


            # Network communication with Stripe failed
            
        except stripe.error.StripeError as e:
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

            # Display a very generic error to the user, and maybe send
            # yourself an email
            
        except Exception as e:
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

            # Something else happened, completely unrelated to Stripe
            
        
        
        
        return redirect("/payment/stripe/")

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
