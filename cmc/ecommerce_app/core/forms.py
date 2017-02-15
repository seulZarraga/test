# coding=utf-8

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from core.models import CustomUser

import sendgrid
from django.conf import settings

from django.core.urlresolvers import reverse


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name', 'telephone', 'second_last_name',)


class CustomSetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control input-lg',
                                                                      'placeholder': mark_safe(
                                                                          "New password")}))
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'class': 'form-control input-lg',
                                                                      'placeholder': mark_safe(
                                                                          "Confirm password")}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=True, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):

        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        usermodel = get_user_model()
        email = self.cleaned_data["email"]
        port = ""

        active_users = usermodel._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                port = request.META['SERVER_PORT']
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                'port': port,
            }

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            token = token_generator.make_token(user)

            reset_url = "https://" + domain + (reverse('core.views.password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
            sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)
            message = sendgrid.Mail()
            message.add_to(str(user.get_full_name()) + ' <' + user.email + '>')
            message.set_html('Body')
            message.set_text('Body')
            message.set_subject('Restablecer Contraseña')
            message.set_from('CMC <ingzarragaespinosa@gmail.com>')

            # You pass substitutions to your template like this
            message.add_substitution('-first_name-', user.first_name)

            message.add_substitution('-reset_url-', reset_url)

            # Turn on the template option
            message.add_filter('templates', 'enable', '1')

            # Tell SendGrid which template to use
            message.add_filter('templates', 'template_id', '3a0ebfd3-aaaa-44ba-a235-7d7b062597dc')

            # Get back a response and status
            status, msg = sg.send(message)
