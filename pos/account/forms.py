from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate



class UserAuthenticationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']

            if not authenticate(username=username, password=password):
                raise forms.ValidationError("Invalid Login Credentials")