from jose.constants import ALGORITHMS

EXPIRATION_MINUTES = 60
SECRET_KET = 'this_is_my_secret'
JWT_ALGO = ALGORITHMS.HS256
ALLOWED_USERS_PASSWORDS = {
    'david': "1234",
    'israel': "1234",
    'dror': "1234",
    'shay': "1234"
}
