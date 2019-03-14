# -*- coding: utf-8 -*-
from foundation import constants


def constants(request):
    """
    Context processor will attach all our constants to every template.
    """
    return {
        'CONSTANTS': constants
    }
