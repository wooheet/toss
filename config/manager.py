import jwt
import base64
import json
import logging
import secrets
import aiobotocore
from django.conf import settings
from botocore.client import Config
from datetime import timedelta
from django.utils import timezone
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class TokenManager:

    token = None
    refresh_token = None
    _cntry = None
    _algorithm = None
    _jwt_exp_timedelta = None

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
        jwt_token = cls.create_jwt(0, 'duid')
        cls.verify(jwt_token)

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
        cls.refresh_token = secrets.token_urlsafe(32)
        return cls.refresh_token

    @classmethod
    def create_jwt(cls, user_id, device_unique_id,
                   jwt_exp_timedelta=None, headers=None):
        """
            Return jwt and refresh token
        """
        if headers is None:
            headers = {}

        if jwt_exp_timedelta is None:
            jwt_exp_timedelta = cls._jwt_exp_timedelta
        # TODO Secretmanager setting
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
        cls.token = encoded_jwt.decode()
        return cls.token


class SecretManager:

    _private = None
    _client = None

    @classmethod
    async def init(cls):
        boto_session = BotoSession.get()
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


class BotoSession:

    _session = None
    _default_config = None

    @classmethod
    async def init(cls):
        if cls._session is None:
            cls._session = aiobotocore.get_session()

    @classmethod
    async def clear(cls):
        pass

    @classmethod
    def get(cls):
        if cls._session is None:
            cls.init()

        return cls._session

    @classmethod
    def get_config(cls):
        if cls._default_config is None:
            cls._default_config = Config(
                connect_timeout=5,
                read_timeout=5,
                retries={'max_attempts': 2},
                max_pool_connections=5
            )

        return cls._default_config