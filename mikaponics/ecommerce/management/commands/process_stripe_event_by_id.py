# -*- coding: utf-8 -*-
"""
Example:
python manage.py process_stripe_events
"""
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.db.models import Q
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from djmoney.money import Money
from oauthlib.common import generate_token

from ecommerce.models import Store, Product, Shipper, Order, StripeEvent
from foundation.models import User


class Command(BaseCommand):
    """
    python manage.py process_stripe_event_by_id 1
    """

    help = _('Process the stripe event with our web-application.')

    def add_arguments(self, parser):
        parser.add_argument('event_id' , nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            for event_id in options['event_id']:
                event = StripeEvent.objects.get(id=event_id)
                self.begin_processing(event)
        except StripeEvent.DoesNotExist:
            raise CommandError(_('Stripe event ID does not exist.'))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(_('MIKAPONICS: Successfully finished.'))
        )

    def begin_processing(self, event):
        if "account" in event.type:
            print("account - processing...")

        if "charge" in event.type:
            print("charge - processing...")

        if "customer" in event.type:
            print("customer - processing...")



"""
"account.updated",
"account.application.authorized",
"account.application.deauthorized",
"account.external_account.created",
"account.external_account.deleted",
"account.external_account.updated",
"application_fee.created",
"application_fee.refunded",
"application_fee.refund.updated",
"balance.available",
"charge.captured",
"charge.expired",
"charge.failed",
"charge.pending",
"charge.refunded",
"charge.succeeded",
"charge.updated",
"charge.dispute.closed",
"charge.dispute.created",
"charge.dispute.funds_reinstated",
"charge.dispute.funds_withdrawn",
"charge.dispute.updated",
"charge.refund.updated",
"checkout_beta.session_succeeded",
"coupon.created",
"coupon.deleted",
"coupon.updated",
"customer.created",
"customer.deleted",
"customer.updated",
"customer.discount.created",
"customer.discount.deleted",
"customer.discount.updated",
"customer.source.created",
"customer.source.deleted",
"customer.source.expiring",
"customer.source.updated",
"customer.subscription.created",
"customer.subscription.deleted",
"customer.subscription.trial_will_end",
"customer.subscription.updated",
"file.created",
"invoice.created",
"invoice.deleted",
"invoice.finalized",
"invoice.marked_uncollectible",
"invoice.payment_failed",
"invoice.payment_succeeded",
"invoice.sent",
"invoice.upcoming",
"invoice.updated",
"invoice.voided",
"invoiceitem.created",
"invoiceitem.deleted",
"invoiceitem.updated",
"issuing_authorization.created",
"issuing_authorization.request",
"issuing_authorization.updated",
"issuing_card.created",
"issuing_card.updated",
"issuing_cardholder.created",
"issuing_cardholder.updated",
"issuing_dispute.created",
"issuing_dispute.updated",
"issuing_settlement.created",
"issuing_settlement.updated",
"issuing_transaction.created",
"issuing_transaction.updated",
"order.created",
"order.payment_failed",
"order.payment_succeeded",
"order.updated",
"order_return.created",
"payment_intent.amount_capturable_updated",
"payment_intent.created",
"payment_intent.payment_failed",
"payment_intent.succeeded",
"payout.canceled",
"payout.created",
"payout.failed",
"payout.paid",
"payout.updated",
"plan.created",
"plan.deleted",
"plan.updated",
"product.created",
"product.deleted",
"product.updated",
"recipient.created",
"recipient.deleted",
"recipient.updated",
"reporting.report_run.failed",
"reporting.report_run.succeeded",
"reporting.report_type.updated",
"review.closed",
"review.opened",
"sigma.scheduled_query_run.created",
"sku.created",
"sku.deleted",
"sku.updated",
"source.canceled",
"source.chargeable",
"source.failed",
"source.mandate_notification",
"source.refund_attributes_required",
"source.transaction.created",
"source.transaction.updated",
"topup.canceled",
"topup.created",
"topup.failed",
"topup.reversed",
"topup.succeeded",
"transfer.created",
"transfer.reversed",
"transfer.updated",
"issuer_fraud_record.created",
"payment_intent.requires_capture",
"subscription_schedule.canceled",
"subscription_schedule.completed",
"subscription_schedule.created",
"subscription_schedule.released",
"subscription_schedule.updated",
"""
