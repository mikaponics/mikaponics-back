# -*- coding: utf-8 -*-
import datetime
import csv
import pytz

from dateutil import parser
from djmoney.money import Money
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.db.models.functions import Extract
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from foundation.models import Instrument, TimeSeriesDatum


"""
Code below was taken from:
https://docs.djangoproject.com/en/2.0/howto/outputting-csv/
"""




class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def time_series_data_streaming_csv_view(request):
    # Get our user parameters.
    naive_from_dt = request.GET.get('from_dt', None)
    naive_to_dt = request.GET.get('to_dt', None)
    instrument_id = request.GET.get('instrument_id', None)

    # Defensive code:
    if naive_from_dt is None:
        raise SuspiciousOperation("Invalid request - you must include `naive_from_dt` URL parameter.")
    if naive_to_dt is None:
        raise SuspiciousOperation("Invalid request - you must include `naive_to_dt` URL parameter.")
    if instrument_id is None:
        raise SuspiciousOperation("Invalid request - you must include `instrument_id` URL parameter.")

    # Convert our datatime `string` into a `datatime` object.
    naive_from_dt = parser.parse(naive_from_dt)
    naive_to_dt = parser.parse(naive_to_dt)

    # Get the instrument.
    instrument = Instrument.objects.filter(id=int(instrument_id)).first()

    # Convert our naive datetimes to the aware datetimes based on the specific
    # timezone of the tenant.
    local_timezone = pytz.timezone(instrument.device.timezone)
    aware_from_dt = naive_from_dt.astimezone(local_timezone) # Convert to local timezone.
    aware_to_dt = naive_to_dt.astimezone(local_timezone) # Convert to local timezone.

    # Run our filter lookup.
    data = TimeSeriesDatum.objects.filter(
        Q(instrument=instrument) &
        Q(timestamp__range=(aware_from_dt,aware_to_dt))
    ).order_by(
        '-id'
    ).prefetch_related(
        'instrument',
    )

    # # Generate our new header.
    # rows = ([],)

    # Generate the CSV header row.
    rows = ([
        "Value ("+instrument.get_unit_of_measure()+")",
        "Timestamp",
    ],)

    # Generate hte CSV data.
    for datum in data.iterator():
        # Generate the row.
        rows += ([
            datum.value,
            datum.timestamp,
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="time_series_data.csv"'
    return response
