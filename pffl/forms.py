from django import forms

from django.contrib.auth.models import User
from .models import *

register_errors = {
	'required': 'is required',
	'invalid': 'is not valid'
}

class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length = 20, required = True,
	widget=forms.TextInput(attrs={'placeholder': 'first name'}),
	error_messages = register_errors, label = 'first name')

	email = forms.CharField(max_length = 20, required = True, 
	widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
	error_messages = register_errors, label = 'email')

	last_name = forms.CharField(max_length = 20, required = True,
	widget=forms.TextInput(attrs={'placeholder': 'last name'}),
	error_messages = register_errors, label = 'last name')

	password1 = forms.CharField(max_length = 200, required = True,
	widget = forms.PasswordInput(attrs={'placeholder': 'password'}),
	error_messages = register_errors, label = 'password')

	password2 = forms.CharField(max_length = 200, required = True, 
	widget = forms.PasswordInput(attrs={'placeholder': 'confirm'}),
	error_messages = register_errors, label = 'password confirmation')


	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super(RegistrationForm, self).clean()

		# Confirms that the two password fields match
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("passwords do not match")

		# Generally return the cleaned data we got from our parent.
		return cleaned_data


	# Customizes form validation for the username field.
	def clean_email(self):
		# Confirms that the username is not already present in the
		# User model database.
		email = self.cleaned_data.get('email')
		if User.objects.filter(email__exact=email):
			raise forms.ValidationError("already exists")

		# Generally return the cleaned data we got from the cleaned_data
		# dictionary
		return email

