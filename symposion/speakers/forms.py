from django import forms

from django.contrib import messages

from pinax.apps.account.forms import SignupForm as PinaxSignupForm

from emailconfirmation.models import EmailAddress

from markitup.widgets import MarkItUpWidget

from symposion.speakers.models import Speaker


class SpeakerForm(forms.ModelForm):
    
    class Meta:
        model = Speaker
        exclude = ["user", "annotation", "invite_email", "invite_token"]
        widgets = {
            "biography": MarkItUpWidget(),
        }
    
    def clean_twitter_username(self):
        value = self.cleaned_data["twitter_username"]
        if value.startswith("@"):
            value = value[1:]
        return value


class SignupForm(PinaxSignupForm):
    
    def save(self, speaker, request=None):
        # don't assume a username is available. it is a common removal if
        # site developer wants to use email authentication.
        username = self.cleaned_data.get("username")
        email = self.cleaned_data["email"]
        new_user = self.create_user(username)
        if speaker.invite_email == new_user.email:
            # already verified so can just create
            EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
        else:
            if request:
                messages.info(request, u"Confirmation email sent to %(email)s" % {"email": email})
            EmailAddress.objects.add_email(new_user, email)
            new_user.is_active = False
            new_user.save()
        self.after_signup(new_user)
        return new_user
