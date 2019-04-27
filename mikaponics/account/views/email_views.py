# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import condition

from foundation import constants
from foundation.models import User
from foundation.utils import reverse_with_full_domain


logger = logging.getLogger(__name__)


def reset_password_email_page(request, pr_access_code=None):
    # Find the user or error.
    try:
        me = User.objects.get(pr_access_code=pr_access_code)
        if not me.has_pr_code_expired():
            # Indicate that the account is active.
            me.was_activated = True
            me.save()
        else:
            # Erro message indicating code expired.
            logger.info("Access code expired.")
            raise PermissionDenied(_('Access code expired.'))
    except User.DoesNotExist:
        logger.info("Wrong access code.")
        raise PermissionDenied(_('Wrong access code.'))

    # Generate the data.
    url = settings.MIKAPONICS_FRONTEND_HTTP_PROTOCOL+settings.MIKAPONICS_FRONTEND_HTTP_DOMAIN+"/reset-password/"+str(pr_access_code)
    web_view_url = reverse_with_full_domain(
        reverse_url_id='mikaponics_reset_password_email',
        resolve_url_args=[pr_access_code]
    )
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'me': me
    }

    # DEVELOPERS NOTE:
    # - When copying the "Sunday" open source email theme into our code, we will
    #   need to use a formatter to inline the CSS.
    # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'account/email/reset_password_email_view.html', param)


def user_activation_email_page(request, pr_access_code=None):
    # Find the user or error.
    try:
        me = User.objects.get(pr_access_code=pr_access_code)
        if not me.has_pr_code_expired():
            # Indicate that the account is active.
            me.was_activated = True
            me.save()
        else:
            # Erro message indicating code expired.
            logger.info("Access code expired.")
            raise PermissionDenied(_('Access code expired.'))
    except User.DoesNotExist:
        logger.info("Wrong access code.")
        raise PermissionDenied(_('Wrong access code.'))

    # Generate the data.
    url = settings.MIKAPONICS_FRONTEND_HTTP_PROTOCOL+settings.MIKAPONICS_FRONTEND_HTTP_DOMAIN+"/activate/"+str(pr_access_code)
    web_view_url = reverse_with_full_domain(
        reverse_url_id='mikaponics_activate_email',
        resolve_url_args=[pr_access_code]
    )
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'me': me
    }

    # DEVELOPERS NOTE:
    # - When copying the "Sunday" open source email theme into our code, we will
    #   need to use a formatter to inline the CSS.
    # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'account/email/user_activation_email_view.html', param)


def user_was_created_email_page(request, user_id):
    # Find the user or error.
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.info("Wrong access code.")
        raise PermissionDenied(_('Wrong user ID.'))

    # Generate the data.
    web_view_url = reverse_with_full_domain(
        reverse_url_id='mikaponics_user_was_created_email',
        resolve_url_args=[user.id]
    )
    param = {
        'constants': constants,
        'web_view_url': web_view_url,
        'user': user
    }

    # DEVELOPERS NOTE:
    # - When copying the "Sunday" open source email theme into our code, we will
    #   need to use a formatter to inline the CSS.
    # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'account/email/user_was_created_email.html', param)
