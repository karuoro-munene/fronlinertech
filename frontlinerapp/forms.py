from django import forms
from django.contrib.auth.forms import UserCreationForm
from frontlinerapp.models import CustomUser


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=64)
    username = forms.CharField(max_length=32)
    country = forms.CharField(max_length=100)
    phonenumber = forms.CharField(max_length=100)
    password1=forms.CharField()
    password2=forms.CharField()

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

