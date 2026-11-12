# Welcome to Secure Code Game Season-1/Level-5!

# This is the last level of our first season, good luck!

import secrets
import os
import bcrypt

class Random_generator:

    # generates a random token
    def generate_token(self, length=8, alphabet=(
    '0123456789'
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )):
        return ''.join(secrets.choice(alphabet) for i in range(length))

    def generate_salt(self, rounds=12):
        return bcrypt.gensalt(rounds=rounds)


class SHA256_hasher:

    def password_hash(self,password,salt):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('ascii')

    def password_verification(self,password,password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('ascii'))

    

class MD5_hasher:
    def password_hash(self, password):
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('ascii')

    def password_verification(self, password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('ascii'))


# a collection of sensitive secrets necessary for the software to operate
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

PASSWORD_HASHER = 'Bcrypt_hasher'

# Contribute new levels to the game in 3 simple steps!
# Read our Contribution Guideline at github.com/skills/secure-code-game/blob/main/CONTRIBUTING.md