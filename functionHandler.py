import random, string


def genKey():
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
    return key

def genCode():
    code = ''.join(random.choices(string.digits, k=16))
    return code