import random
import logging

from django.utils import crypto
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction, IntegrityError
from core import models as core_models
from django.core.exceptions import ValidationError
from config.utils import ChoiceEnum
from config import db

logger = logging.getLogger(__name__)


class User(AbstractUser, core_models.TimeStampedModel):
    """ Custom User Model """

    class Language(ChoiceEnum):
        LANGUAGE_ENGLISH = "en"
        LANGUAGE_KOREAN = "kr"

    class Currency(ChoiceEnum):
        CURRENCY_USD = "USD"
        CURRENCY_KRW = "KRW"

    language = models.CharField(choices=Language.choices(), max_length=2, blank=True, null=True)
    currency = models.CharField(choices=Currency.choices(), max_length=3, blank=True, null=True)

    USERNAME_FIELD = "username"  # e.g: "username", "email"
    EMAIL_FIELD = "email"  # e.g: "email", "primary_email"

    objects = db.BaseUserManager()

    @classmethod
    def pre_signup(cls, params):
        nickname = params.get('nickname', None)
        first_name = params.get('first_name', '')
        last_name = params.get('last_name', '')
        email = params.get('email', '')
        profile_url = params.get('profile_url')
        username = f'{nickname}{str(timezone.now().timestamp())}'

        if profile_url is not None and len(profile_url) > 255:
            profile_url = None

        if len(first_name) > 30:
            first_name = first_name[:30]

        try:
            with transaction.atomic():
                signup_user = cls.objects.create(
                    first_name=first_name, last_name=last_name,
                    username=username, email=email
                )

                if not nickname:
                    nickname = DefaultNickname.get_default_nickname()

                Profile.objects.create(
                    user=signup_user, nickname=nickname,
                    profile_url=profile_url, country='KR'
                )

        except ValidationError:
            raise ValidationError('User data is invalid.')
        except IntegrityError:
            signup_user = cls.objects.get(username=username)

        return signup_user

    @classmethod
    @transaction.atomic
    def post_signup(cls, request):
        signup_user = request.user

        return signup_user


class Profile(models.Model):

    class CanNotRequestVerifyBadge(Exception):
        pass

    class Gender(ChoiceEnum):
        UNKNOWN = -1
        MALE = 0
        FEMALE = 1
        PREFER_NOT_TO_SAY = 2

    class VerifyStatus(ChoiceEnum):
        REJECTED = -1
        REQUESTED = 0
        REVIEWING = 1
        VERIFIED = 2

    user = models.OneToOneField('users.User', on_delete=models.CASCADE,
                                unique=True, related_name='profile')
    nickname = models.CharField(max_length=100)
    description = models.CharField(max_length=200, default='', blank=True,
                                   help_text='Note: 사용자 프로필 추가 정보')
    gender = models.IntegerField(default=Gender.UNKNOWN.value,
                                 choices=Gender.choices(),
                                 help_text='Note: 성별')
    date_of_birth = models.DateField(null=True,
                                     help_text='Note: 생년월일 (예 1980.12.08')
    profile_url = models.CharField(max_length=255, default='', null=True,
                                   blank=True, help_text='Note: 사용자 프로필 Url')
    country = models.CharField(max_length=4, default=None, null=True,
                               help_text='Country code')
    created = models.DateTimeField(default=timezone.now, blank=True, null=True)

    objects = db.BaseManager()


class DefaultNickname(models.Model):
    class NicknameType(ChoiceEnum):
        PREFIX = 'prefix'
        SUFFIX = 'sufix'

    type = models.CharField(max_length=10, choices=NicknameType.choices())
    word = models.CharField(max_length=100)
    gender = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)

    objects = db.BaseManager()

    @classmethod
    def get_prefix(cls):
        prefixes = cls.objects.filter(type='prefix')
        prefix = random.choice(prefixes)
        return prefix

    @classmethod
    def get_suffix(cls, prefix):
        suffixes = cls.objects.filter(type='suffix', gender=prefix.gender).cache()
        suffix = random.choice(suffixes)
        return suffix

    @classmethod
    def get_nickname(cls):
        try:
            base_nickname = '{prefix} {suffix}'
            prefix = cls.get_prefix()
            suffix = cls.get_suffix(prefix=prefix)
            made_nickname = base_nickname.format(prefix=prefix.word, suffix=suffix.word)

        except Exception:
            logger.exception('Default Nickname Create failed..')
            made_nickname = crypto.get_random_string(length=12)

        return made_nickname

    @classmethod
    def get_default_nickname(cls):
        return 'toss' + str(timezone.now().timestamp())[3:]