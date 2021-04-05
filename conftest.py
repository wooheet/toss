import jwt
from django.urls import reverse
from datetime import datetime, timedelta
from rest_framework.test import APIClient, APITestCase
from config import settings
from users.models import User


class AuthAPITestCase(APITestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_token = "1"
        self.device_token = "test-device-token"

    def _make_pre_signup_data(self, nickname):
        pre_signup_data = {
            "nickname": nickname,
            "first_name": "first_name",
            "last_name": "last_name",
            "profile_url": "picture",
            "email": "{}@mail.com".format(nickname),
        }
        return pre_signup_data

    def signup_user(self, **kwargs):
        nickname = kwargs.get("nickname", "name")

        client = APIClient()
        client.credentials(HTTP_USER_AGENT="AuthServer")

        pre_signup_data = self._make_pre_signup_data(nickname)

        res = client.post(
            reverse("user-list"),
            pre_signup_data,
            format="json",
            HTTP_X_FORWARDED_HOST='settings.URL_WEB',
        )

        user_id = res.data.get("results")[0].get("user_id")

        data = {
            "sub": user_id,
            "did": "testdeviceuniqueid",
            "exp": int((datetime.now() + timedelta(days=100)).timestamp()),
        }

        self.jwt_token = jwt.encode(
            data, settings.AUTH_SERVER_PRIVATE_KEY, algorithm="RS256"
        ).decode("utf-8")

        return self.jwt_token
        # client.credentials(HTTP_AUTHORIZATION="Bearer %s" % self.jwt_token)
        #
        # signup_data = {
        #     "id_token": self.id_token,
        #     "os_type": os_type,
        #     "model_name": "{}_model_name".format(nickname),
        #     "device_token": token,
        #     "country": 'kr',
        #     "service_agreement": {
        #         "service_terms": True,
        #         "personal_info_col": True,
        #         "personal_info_exp": True,
        #         "device_access": True,
        #         "marketing": True,
        #         "marketing_email": True,
        #         "night_push_agree": True,
        #         "birth_gender_nickname_col": True,
        #     },
        # }
        #
        # res = client.post(
        #     reverse("user-new-signup"), signup_data, format="json"
        # )
        #
        # client_data = res.data.get("results")[0]
        # client_data.update(
        #     os_type=os_type, device_token=token
        # )
        #
        # self.user_id = client_data.get("id")
        #
        # return client_data, client

    def setUp(self, **kwargs):
        # super().setUp()
        # self.user, self.client = self.signup_user(**kwargs)
        # self.no_signup_client = APIClient()
        super().setUp()
        self.signup_user(**kwargs)

    def many_signup(self, count):
        signup_list = list(
            map(
                lambda x: self.signup_user(nickname=f"user{x}"), range(0, count)
            )
        )
        user_list = []
        client_list = []
        for u, c in signup_list:
            user_list.append(u)
            client_list.append(c)
        return user_list, client_list

    def get_user(self):
        return User.objects.get(id=self.user["id"])