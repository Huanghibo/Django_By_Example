from django import forms
from .models import Order
from localflavor.cn.forms import CNProvinceSelect, CNPostCodeField


class OrderCreateForm(forms.ModelForm):
    city = CNProvinceSelect
    postal_code = CNPostCodeField

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']