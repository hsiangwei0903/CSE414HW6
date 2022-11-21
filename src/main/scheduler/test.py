def valid_password(password):
    if len(password)<8:
        print('password should be at least 8 characters long.')
        return False
    if password.islower() or password.isupper():
        print('password should contain both upper and lower case character.')
        return False
    if not any(c in '!@#?' for c in password):
        print('password should contain at least one special character from !@#?.')
        return False
    return True

print(valid_password('123abcdefG'))

import datetime

date = '12-3-1999'

date_tokens = date.split("-")
month = int(date_tokens[0])
day = int(date_tokens[1])
year = int(date_tokens[2])
d = datetime.datetime(year, month, day)
print(d)
print(type(d))