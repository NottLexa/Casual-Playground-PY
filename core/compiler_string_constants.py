whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
naming = digits + ascii_letters
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = naming + punctuation + whitespace

s_dig = set(digits)
s_digdot = s_dig | set('.')
s_ascl = set(ascii_lowercase)
s_ascu = set(ascii_uppercase)
s_asc = s_ascl | s_ascu
s_nam = s_dig | s_asc