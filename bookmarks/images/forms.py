from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django import forms
from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {'url': forms.HiddenInput, }

    # 自定义以clean_<fieldname>形式命名的表单方法实现清洁特定的字段，这个方法会在表单实例执行is_valid()时执行
    # 需要的时候，可以在清洁方法中改变字段的值或者为特定的字段抛出错误
    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('图片地址不合法')
        return url

    # ModelForm提供save()方法来保存目前的模型实例到数据库中，并且返回一个对象
    # save()方法接受布尔参数commit，这个参数允许你指定这个对象是否要被储存到数据库中
    # 如果commit是False，save()方法将会返回模型实例但并不会把这个对象保存到数据库中
    def save(self, force_insert=False, force_update=False, commit=True):
        # 从表单中新建image对象，并且设置commit=False
        image = super(ImageCreateForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        # 根据title生成slug，再提取URL里面的后缀，合并为新文件名
        image_name = '{}.{}'.format(slugify(image.title), image_url.rsplit('.', 1)[1].lower())
        # 从给定的 URL 下载图片，如果对方限制了referer则只能返回防盗链图
        response = request.urlopen(image_url)
        # ImageField的save()方法，第一个参数是保存的文件名，第二个参数是ContentFile对象，里面的内容是要上传的图片、视频的二进制内容
        image.image.save(image_name, ContentFile(response.read()), save=False)
        # 在save()方法的commit参数为True时保存表单到数据库中
        if commit:
            image.save()
        return image
