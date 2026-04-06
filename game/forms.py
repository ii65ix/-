from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile


class StyledLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم / Username",
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "class": "auth-input"}
        ),
    )
    password = forms.CharField(
        label="كلمة المرور / Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "class": "auth-input"}
        ),
    )


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "اسم المستخدم / Username"
        self.fields["username"].widget.attrs.update(
            {"autocomplete": "username", "class": "auth-input"}
        )
        self.fields["password1"].label = "كلمة المرور / Password"
        self.fields["password1"].widget.attrs.update({"class": "auth-input"})
        self.fields["password2"].label = "تأكيد كلمة المرور / Confirm password"
        self.fields["password2"].widget.attrs.update({"class": "auth-input"})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio",)
        labels = {"bio": "نبذة عنك / Bio"}
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "auth-input",
                    "placeholder": "اكتب نبذة قصيرة عنك…",
                }
            ),
        }
