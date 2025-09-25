from django import forms
from .models import NewsletterSubscriber, ContactMessage

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email address...',   # Match Ashar template
                'class': 'form-control',
                'aria-label': 'Email address',
                'aria-describedby': 'button-subscribe',
            }),
        }




class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your Email"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"class": "form-control", "placeholder": "Message", "rows": 5}),
        }
