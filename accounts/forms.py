from django import forms

class LoginForm(forms.Form):
    username= forms.CharField(max_length=250)
    password= forms.CharField(widget=forms.PasswordInput)
