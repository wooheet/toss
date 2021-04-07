import jwt
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from conftest import AuthAPITestCase


class TestAuthUserAPI(AuthAPITestCase):
    """
        로그인 사용자 API
    """

    def setUp(self):
        super().setUp()

    def test_signin_with_jwt(self):
        res = self.client.post(
            reverse('user-signin'), format='json'
        )
        self.assertEqual(res.status_code, 200)
        res_data = res.data.get('results')[0]
        self.assertEqual(res_data.get('email'), 'name@mail.com')

    def test_signin_wrong_jwt_token(self):
        normal_credentials = self.client._credentials['HTTP_AUTHORIZATION']

        self.client._credentials['HTTP_AUTHORIZATION'] = \
            'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ' \
            '9.eyJzdWIiOjJ9.hTWc0Hv8AZTzkNUwRZkGVzGvt7j' \
            '6WDTbbW_VB81SMiKA8yJNoDYUwkELGGD7iHPsPSB-3U2Na_6Ja78B1Ypn'

        res = self.client.post(
            reverse('user-signin'), format='json'
        )
        self.assertEqual(res.status_code, 401)

        self.client._credentials['HTTP_AUTHORIZATION'] = normal_credentials

        res = self.client.post(
            reverse('user-signin'), format='json'
        )
        self.assertEqual(res.status_code, 200)

    def test_sigin_jwt_token_expire(self):
        res = self.client.post(
            reverse('user-signin'), format='json'
        )
        self.assertEqual(res.status_code, 200)

        user_id = self.user.get('id')

        data = {
            'sub': user_id,
            'did': 'testdeviceuniqueidforexpiredtoken',
            'exp': int((timezone.now() - timedelta(days=1)
                        ).timestamp())
        }

        expired_token = jwt.encode(data, self.keys['private'],
                                   algorithm='RS256').decode('utf-8')
        self.client._credentials['HTTP_AUTHORIZATION'] = "Bearer %s" % expired_token

        res = self.client.post(
            reverse('user-signin'), format='json'
        )
        self.assertEqual(res.status_code, 460)

    def test_create_jwt_token(self):
        res = self.client.post(
            reverse('user-token'), format='json'
        )
        self.assertEqual(res.status_code, 200)
