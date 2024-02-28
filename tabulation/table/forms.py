from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
class TabelForm(ModelForm):
    class Meta:
        model = Employees
        fields = "__all__"

        
class SubdivisionForm(forms.Form):
    subdivisions = Subdivision.objects.all()
    name_choices = [(subdivision.name, subdivision.name) for subdivision in subdivisions]
    name = forms.Select(choices=name_choices)


class ReservoirForm(forms.Form):
    oil_places = OilPlace.objects.all()
    name_choices = [(oil_place.name, oil_place.name) for oil_place in oil_places]
    name = forms.Select(choices=name_choices)

class TabelReservoirForm(forms.Form):
    oil_places = OilPlace.objects.all()
    name_choices = [(oil_place.name, oil_place.name) for oil_place in oil_places]
    name = forms.Select(choices=name_choices)

class TabelSubdivisionForm(forms.Form):
    subdivisions = Subdivision.objects.all()
    name_choices = [(subdivision.name, subdivision.name) for subdivision in subdivisions]
    name = forms.Select(choices=name_choices)

class TabelYearForm(ModelForm):
    class Meta:
        model = Tabel
        fields = ['year']



#login start
UserModel = get_user_model()
from django.utils.text import capfirst

"Try Custon Auth Form start"

class UserLoginForm(forms.Form):
    
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }
    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)


        
    def clean(self):
        cleaned_data = super().clean()
        username_part_email = cleaned_data.get("email")
        username_part=username_part_email.split('@')
        username = username_part[0]
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email is not None and password:
            user = authenticate(self.request, email=email, password=password,username=username)

            if user is None:
                raise ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

            self.confirm_login_allowed(user)

        return cleaned_data
    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            # params={"email": self.fields['email'].verbose_name},
        )

"Try Custon Auth Form end"





#Custom Admin Panel Authentication
    
class AdminUsernameAuthenticationForm(AuthenticationForm):
    def __init__(self,*args, **kwargs):
        super(AdminUsernameAuthenticationForm,self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user_model = self.user_cache._meta.model
            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist:
                raise forms.ValidationError('Invalid username or password')

            if not user.check_password(password):
                raise forms.ValidationError('Invalid username or password')

        return self.cleaned_data
        

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            UserModel = get_user_model()

            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                raise forms.ValidationError('Invalid email or password')

            if not user.check_password(password):
                raise forms.ValidationError('Invalid email or password')

            self.user = user

        return super().clean()        

#login end

