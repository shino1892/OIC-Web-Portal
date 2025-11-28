import jwt
import datetime
from app.core.config import Config

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    """
    JWTアクセストークンを生成する
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        # デフォルトの有効期限（例: 15分）
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """
    JWTアクセストークンを検証・デコードする
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # 有効期限切れ
        return None
    except jwt.InvalidTokenError:
        # 無効なトークン
        return None