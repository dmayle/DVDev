"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
from webhelpers.html.secure_form import secure_form as form
from webhelpers.html.tags import end_form, submit, text, textarea
from routes.util import url_for