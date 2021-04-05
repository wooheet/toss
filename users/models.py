from django.contrib.auth.models import AbstractUser
from django.db import models, transaction, IntegrityError
from core import models as core_models
from django.core.exceptions import (
    ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
)


class User(AbstractUser, core_models.TimeStampedModel):
    """ Custom User Model """

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"

    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )

    LANGUAGE_ENGLISH = "en"
    LANGUAGE_KOREAN = "kr"

    LANGUAGE_CHOICES = ((LANGUAGE_ENGLISH, "English"),
                        (LANGUAGE_KOREAN, "Korean"))

    CURRENCY_USD = "usd"
    CURRENCY_KRW = "krw"

    CURRENCY_CHOICES = ((CURRENCY_USD, "USD"), (CURRENCY_KRW, "KRW"))

    avatar = models.ImageField(upload_to="avatars", blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(blank=True)
    birthdate = models.DateField(blank=True, null=True)
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=2, blank=True)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3, blank=True)
    superhost = models.BooleanField(default=False)
    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")

    USERNAME_FIELD = "username"  # e.g: "username", "email"
    EMAIL_FIELD = "email"  # e.g: "email", "primary_email"

    @classmethod
    def pre_signup(cls, params):
        # SpoonUser / Profile 만 생성
        # 성별 / 생년월일은 나중에 post_signup 때 data 가 들어옴 그래서 가입할때 None 처리
        # nick_name 또한 post_signup 에서 data 가 들어오면 update
        sns_type = params.get('sns_type')
        sns_id = params.get('sns_id')
        nickname = params.get('nickname', None)
        first_name = params.get('first_name', '')
        last_name = params.get('last_name', '')
        email = params.get('email', '')
        profile_url = params.get('profile_url')
        country = params.get('country', '')
        username = params.get('tid', f'{sns_type}.{sns_id}')

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

                # if not nickname:
                #     nickname = DefaultNickname.get_default_nickname()
                #
                # if UnfitWord.check_unfit(word=nickname, to_nickname=True):
                #     nickname = DefaultNickname.get_default_nickname()

                # Profile 생성
                # Profile.objects.create(
                #     user=signup_user, nickname=nickname, tag=signup_user.get_tag(),
                #     profile_url=profile_url, country=country,
                #     is_public_like=False, is_public_cast_storage=False,
                # )

        except ValidationError:
            raise ValidationError('User data is invalid.')
        except IntegrityError:
            signup_user = cls.objects.get(username=username)

        return signup_user


