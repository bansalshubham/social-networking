
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    
    def __init__(self, *args, **kwargs):
        ...