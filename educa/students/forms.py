from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):
    #  course字段是学生报名的课程，所以它是ModelChoiceField
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.HiddenInput)
