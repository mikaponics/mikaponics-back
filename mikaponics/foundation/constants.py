import pytz


TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


COUNTRY_PROVINCE_CODES = {
    'Canada': {
        'Newfoundland and Labrador': 'NL',
        'Prince Edward Island': 'PE',
        'Nova Scotia': 'NS',
        'New Brunswick': 'NB',
        'Quebec': 'QC',
        'Ontario': 'ON',
        'Manitoba': 'MB',
        'Saskatchewan': 'SK',
        'Alberta': 'AB',
        'British Columbia': 'BC',
        'Yukon': 'YT',
        'Northwest Territories': 'NT',
        'Nunavut': 'NU',
    },
}


MIKAPONICS_DEFAULT_PRODUCT_ID = 1
MIKAPONICS_SOIL_PRODUCT_ID = 1
MIKAPONICS_HYDROPONICS_PRODUCT_ID = 2
MIKAPONICS_AQUAPONICS_PRODUCT_ID = 3
MIKAPONICS_ALGAE_PRODUCT_ID = 4
MIKAPONICS_AUTHORIZED_DEVICE_PRODUCT_ID = 5
MIKAPONICS_DEFAULT_SUBSCRIPTION_ID = 1
MIKAPONICS_DEFAULT_SHIPPER_ID = 1
