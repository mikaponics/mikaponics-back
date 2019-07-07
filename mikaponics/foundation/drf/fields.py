
from rest_framework import exceptions, serializers


class BlankableFloatField(serializers.FloatField):
    """
    If field receives an empty string ('') for a float field then turn it into
    a None number.
    """
    def to_internal_value(self, data):
        if data == '':
            return None

        return super(BlankableFloatField, self).to_internal_value(data)
