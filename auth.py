import jwt
import datetime

SECRET ="my_ultra_secure_crypto_project_secret_key_2026_!!!"

def create_token(user):
    payload = {
        "user": user,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
        return decoded["user"]
    except:
        return None