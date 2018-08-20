from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    # 添加额外字段
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='重复密码', widget=forms.PasswordInput)
    captcha = CaptchaField(label='验证码')

    class Meta:
        model = User
        # 这些字段会在它们对应的model字段上进行验证，例如：如果用户输入已经存在的用户名，将会得到验证错误的提示
        fields = ('username', 'email')
        # 指定不需要的字段
        # exclude = ['pub_time', 'enabled']

    # 检查第二次输入的密码是否和第一次输入的保持一致，通过调用 is_valid() 方法验证这个form时这个检查会被执行
    # 可以提供clean_<fieldname>()方法给任何form字段用来清理值或者抛出from指定的字段的验证错误
    # forms还包含clean()方法用来验证form的所有内容，这对验证需要依赖其他字段的字段是非常有用的
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('2次输入的密码不匹配')
        return cd['password2']


class LoginForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput)
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput)
    captcha = CaptchaField(label='验证码')


class UserEditForm(forms.ModelForm):
    class Meta:
        # 允许用户编辑它们的 first name,last name, e-mail 这些储存在 User 模型中的内置字段
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        # 允许用户编辑存储在 Profile 模型中的额外数据，用户可以编辑他们的生日数据以及上传一张照片。
        model = Profile
        fields = ('date_of_birth', 'photo')
