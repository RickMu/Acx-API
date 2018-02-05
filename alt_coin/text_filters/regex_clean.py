import re

TEXT ='text'
URL_PATTERN = re.compile(r'(https?://[^\s]+)')
NL_PATTERN = re.compile(r'(\n)')
NL_PATTERN = re.compile(r'([,.\'\n\t\r-?!+])')




def remove_special_char(text):

    text = URL_PATTERN.sub(' ',text)
    text = NL_PATTERN.sub(' ',text)
    return text

