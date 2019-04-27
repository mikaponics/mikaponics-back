from foundation.models import User


def get_staff_email_addresses():
    return User.objects.filter(is_staff=True).values_list('email')
