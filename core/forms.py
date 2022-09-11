from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),

    ('P', 'Paypal')

)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(max_length=200,
                                     widget=forms.TextInput(attrs={

                                         "id": "address",
                                         "class": "form-control",
                                         'placeholder': '1234 Main St',
                                     }))
    apartment_address = forms.CharField(max_length=200, required=False,
                                        widget=forms.TextInput(attrs={

                                            "id": "address-2",
                                            "class": "form-control",
                                            'placeholder': 'Apartment or suite',
                                        }))
    # country = CountryField()
    country = CountryField(blank_label='Select Country').formfield(widget=CountrySelectWidget(attrs={

        "class": "custom-select d-block w-100",
        "id": "country",
    }))
    zip = forms.CharField(
        widget=forms.TextInput(attrs={

            "id": "zip",
            "class": "form-control",
            'placeholder': '',
        })
    )
    same_shipping_address = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
