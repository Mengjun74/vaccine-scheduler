import hashlib
import os


class Util:
    def generate_salt():
        # return base64.urlsafe_b64encode(uuid.uuid4().bytes)
        return os.urandom(16)

    def generate_hash(password, salt):
        # t_sha = hashlib.sha512()
        # t_sha.update(password+str(salt))
        # hashed_password = base64.urlsafe_b64encode(t_sha.digest())
        # return hashed_password
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=16
        )
        return key


