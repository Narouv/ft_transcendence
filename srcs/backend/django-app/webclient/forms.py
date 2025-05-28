from django import forms
from api.models import User
from django.contrib.auth.forms import UserCreationForm


class RegistrationForm(UserCreationForm):
	username = forms.CharField(required=True)
	email = forms.EmailField(required=True)
	password1 = forms.CharField(required=True, widget=forms.PasswordInput())
	password2 = forms.CharField(required=True, widget=forms.PasswordInput())
	
	def clean(self):
		cleaned_data = super(UserCreationForm, self).clean()
		password1 = cleaned_data.get("password1")
		password2 = cleaned_data.get("password2")

		if password1 != password2:
			self.add_error("password2", "Passwords do not match")

	class Meta:
		model = User
		fields = [ "username", "email", "password1", "password2" ]