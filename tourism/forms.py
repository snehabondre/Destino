from django import forms
from .models import Mobile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'email',)

    def __init__(self, *args, **kwargs):

        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            username ="username"
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content' :help_text, 'data-placement': 'right',
                     'data-container': 'body'})
                self.fields[username].widget.attrs.update(
                    {'id': username})

                # to ensure that the user email is unique
    # def clean_email(self):
    #     if User.objects.filter(email=self.cleaned_data.get('email', None)).count() > 0:
    #         raise forms.ValidationError("User with this email already exists")

    #     return self.cleaned_data.get('email')

class MobileForm(forms.ModelForm):
    Mobile_Number = forms.CharField(max_length=15,required=True)
    class Meta:
        model = Mobile
        fields = ('Mobile_Number',)


