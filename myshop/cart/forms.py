from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # coerce=int强制转换为整数
    quantity = forms.TypedChoiceField(label='数量', choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    # BooleanField使用python的bool来判断，只要传了任意非空值，都会当做True来处理，
    # 如果传了空值，由于forms.Field默认属性是required=True，会校验失败，所以如果需要可以填False的Field，那么需要手动设置required=False
    # initial声明表单字段的初始值，实例化表单时应该给出映射字段名称到初始值的字典，比如f = ContactForm(initial={'subject': 'Hi there!'})
    # HiddenInput控件表示不展示给用户
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
