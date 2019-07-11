from foundation.models import User


def get_staff_email_addresses():
    '''
    Utility function which fetches all the administrator emails and returns
    a python array of emails.
    '''
    user_emails_queryset = User.objects.filter(is_staff=True).values_list('email')
    user_emails = []
    for email_tuple in user_emails_queryset:
        email_string = str(email_tuple[0]) # Get from tuple and stringify.
        user_emails.append(email_string)
    return user_emails
