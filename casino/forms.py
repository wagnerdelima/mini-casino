from django import forms

from casino.models import CustomerUser


class RegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('password', 'Passwords do not match')

    class Meta:
        model = CustomerUser
        fields = ('username', 'password')
