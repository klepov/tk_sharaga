from Crypto.Hash import MD5


#
# def crypt(passw):
#     return hashlib.sha1(passw.encode()).hexdigest()

def crypt(passw):
    h = MD5.new()
    h.update(passw.encode())
    return h.hexdigest()
