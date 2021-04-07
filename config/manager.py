import base64
import json
from logger import Logger
import settings
import secrets
import jwt
from datetime import timedelta
from django.utils import timezone
from helpers.session import BotoSession
from cryptography.fernet import Fernet

class JwtManager:

    AUTH_TYPE = 'Bearer'

    @classmethod
    async def init(cls):
        cls._jwt_exp_timedelta = timedelta(hours=settings.JWT_EXP)
        cls._algorithm = settings.JWT_ALGORITHM
        cls._cntry = settings.COUNTRY
        cls._validate_jwt()

    @classmethod
    def _validate_jwt(cls):
        # Auth 서버가 정상 기동전, 설정된 키가 유효한지 확인한다.
        jwt = cls.create_jwt(0, 'duid')
        cls.verify(jwt)

    @classmethod
    def _build_payload(cls, user_id, device_unique_id, jwt_exp_timedelta):
        payload = {
            'sub': int(user_id),
            'did': device_unique_id,
            'exp': timezone.now() + jwt_exp_timedelta,
            'iat': timezone.now(),
            'cntry': cls._cntry
        }
        return payload

    @classmethod
    def verify(cls, token):
        public_key = SecretManager.get_public()
        return jwt.decode(token, public_key, algorithms=cls._algorithm)

    @classmethod
    def create_refresh_token(cls):
        return secrets.token_urlsafe(32)

    @classmethod
    def create_jwt(
        cls, user_id, device_unique_id, jwt_exp_timedelta=None, headers=None
    ):
        """
        Return jwt and refresh token
        """
        if headers is None:
            headers = {}

        if jwt_exp_timedelta is None:
            jwt_exp_timedelta = cls._jwt_exp_timedelta

        private_key = SecretManager.get_private()
        payload = cls._build_payload(
            user_id, device_unique_id, jwt_exp_timedelta
        )

        encoded_jwt = jwt.encode(
            payload,
            private_key,
            algorithm=cls._algorithm,
            headers=headers
        )

        return encoded_jwt.decode()


class SecretManager:

    @classmethod
    async def init(cls):
        boto_session = BotoSession.get()
        cls.logger = Logger.get_logger(cls.__name__)
        cls._client = boto_session.create_client(
            'secretsmanager',
            endpoint_url=settings.SECRETS_ENDPOINT_URL
        )
        await cls._update_keys()

    @classmethod
    async def clear(cls, app):
        pass

    @classmethod
    def _decode_key(cls, key, decode=False):
        _key = base64.decodebytes(key.encode())
        if decode is True:
            return _key.decode()
        return _key

    @classmethod
    def _encode_key(cls, key):
        _encoeed_key = base64.encodebytes(key.encode())
        return _encoeed_key

    @classmethod
    async def _update_keys(cls):
        rsp = await cls._client.get_secret_value(
            SecretId=settings.SECRETS_NAME
        )
        keys = json.loads(rsp['SecretString'])
        cls._private = cls._decode_key(keys['private'])
        cls._public = cls._decode_key(keys['public'])
        cls._symmetric = settings.TEMP_ENCRYPT_KEY
        cls._fernet = Fernet(cls._symmetric)

    @classmethod
    def get_private(cls, decode=False):
        if decode is True:
            return cls._private.decode()
        return cls._private

    @classmethod
    def get_public(cls, decode=False):
        if decode is True:
            return cls._public.decode()
        return cls._public

    @classmethod
    def get_symmetric(cls):
        return cls._symmetric

    @classmethod
    def encrypt(cls, data):
        return cls._fernet.encrypt(data.encode()).decode()

    @classmethod
    def decrypt(cls, data):
        return cls._fernet.decrypt(data.encode()).decode()
