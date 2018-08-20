from django import forms


class CouponApplyForm(forms.Form):
    code = forms.CharField(label='优惠码')
