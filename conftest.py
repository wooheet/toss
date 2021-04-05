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
        self.keys = {
            "private": "-----BEGIN RSA PRIVATE KEY-----\n"
                       "MIIJJwIBAAKCAgEAup8gRjJMk4c4vFcu8qYwnjReK13rgqDELvHbSDyuxbJL9koV\n"
                       "c9OGl6oETw1mbIKTsPNZOgfDJTOzHxCjmiLwWe9JlO3T7jfJpvifQIHbfZ7yXJbe\n"
                       "PTpE+RkzWETQXSBbC8TUCe4w0JcWAD5qKUxlab7akfJmrQDR2QYEUOFPAyi/l1UM\n"
                       "RtbJ4tyHQ7J8PREXeAp2I5TjlbTpEtsy2Y7BDfgBr30NSjSvn43nJw6+0dMudvlF\n"
                       "3i4MQLIhLfcTU7XLg7K2ZB0hovRgq7Bnx45KgruDIw18T2yVVJBAPHsyusCcGRdG\n"
                       "QnZzDKlhaJiUc/5UHkN2UDB3zVVZNzm2WCJheoN61VHtVGLjf45On/kggSHScMIT\n"
                       "4yCTwKL0VhEFf/vwSYwXC7Ft6TtWUGrl5G76+oWEXaTFDTLddu8EAln7Mu6r09dq\n"
                       "Fqhsd4MJBlPWTlOErGrIy3xeb/rKgFxmVdnJGynvYvZYDkks8f4M8nxBp0InRrjm\n"
                       "7KzwSewy0p+xMLa5UzrZkjl/xF0Sby48uSGnVdnFNEvPjBSwHMuJl3Btg+i9zi4Y\n"
                       "GMaNMm8otJTX0Hgrso5GyI7moqm8O0g1NhiGw2iF3fZW9Z8uoe8/Z0KebmeoUKw0\n"
                       "dKoxoEHRp2XWeMTcRM+uQCVJrNv8RqbPTynoWoqonFyTWehJ3IZg/Nw2b5cCAwEA\n"
                       "AQKCAgBsEAqDO0sGPk3HGYDQ9xS99zr0R61A9dDEEj5UxPa6+XRtCBcF+9064zMd\n"
                       "h3fgq3fUBgWLycThPN+ixGLHtSWSHjJwb4rBrUIyUlL86nTrd+eFX8MOlzgrOcF2\n"
                       "glpZIow182KI4YkYr/QIbhvREDDFG8O6sS9tTEU3Mvm6z8yN2sGeYpv6RROgLuyQ\n"
                       "ccDpJ4V8eCpSjjt+i8ROq+j0+2mkqhBnyrSwXHO5o1TPVAWAwJVuRQeFEQr9R2hZ\n"
                       "EnH5jhJrj0d4DzpT/sgfgsWFU0qoCuZznLJ31ztdPS5FF12XsEJzcPu5LpeOJGKI\n"
                       "S5ni1MlmwM+4vWgR2TMQ/HUu8bGZXg3mbZibXq8foHgXJmporbRr6f89wnSaFtp1\n"
                       "SWL5ur9YG1VB9I54SoLSaxgxqJQdHYoJzGDOQBE7HTA9iZ6typprZgoO6Jza8egB\n"
                       "yTAOkby+UvonUORHR9Q/n5ajeWB2fY/gDIiDhtt5HuVkni/VD4uCBLN3dU4eEujM\n"
                       "8uV2lyo5VJ8qKhb6uWIWsSwQAa71J4uH1bCdlr9lo2m0W9ECWwajHq4mnS85q9PI\n"
                       "vWp5Gr+ZxjGwTfDNWaLBy40TRvKkgTlrEd6a3pPjnPK7XWXCL9U5nzV8vW3v4gjm\n"
                       "r8ydbOii34YvYt1zIxUvljyoD3aqzmsxjisZ+L4T8QkclOgWmQKCAQEA8vRjZDdb\n"
                       "MjrF42TNr/4D+rnlP8TQ4JcPytWum7AO+iu/amHnvcDNbCiu3dmMWxNslG6NVXUM\n"
                       "B0Q/UNJ/uwtQdeATQKhd4mPdm0HGlJcN6qCpIn531OqDmeuKfjHHPbX7nlxpdiMC\n"
                       "XWOO7UR8aOe3jQ+/uy+bjFtec0AASynFvmt6EGqAnnjepHK9pAie28KZSXm36IJt\n"
                       "Hyr25DovyDQthHjKJaeVAaPBP7nsCOo02ennty5XCN4mn5m9F5N+euH4ij6Q2Vdo\n"
                       "MbpgppbX86OO24zA3xaQ9YpoQkVuJPSdW6aA/Noweh/Yn06guUkBc7Dz1E9eIaZc\n"
                       "CcQ/iOaR9cn2fQKCAQEAxKRkwB8weju1oSyYSa1oDrqhlCoJt+t/ovcTNG+8dHKN\n"
                       "CpSHYYDWGqTRaeXhcHCC/tiGZGjb5LImHAkjTWJrol6To00PAHfYEE0d3HHCf7ym\n"
                       "bVC6BdSlFI7Lv2pO1Xgd7spQVoVBPq4j9IjWVDCYiM0ffn+rP0q51Eg0kp2MP/y7\n"
                       "eKtfLMcdvJW8bsbAHaeLr63MSqKd1VsT+yJRH1BD/tFv9VqB88iQSJQQaoA0yEJJ\n"
                       "u13h4QOqfuDklzDAa0XM6cYn4zHipbCFhQgpGAU0OXssy6iuDKRgab/1tXS/WDJK\n"
                       "0kLlmdIgKkzhaQiZOXraAzfUsefKJkVcV+1DJXrWowKCAQBJIXUVgnAqA3TziLE9\n"
                       "S3nJK9Gsy0KQiAgR5xYi+PDZLvf0Prox7Ooop2pTjxtngsZJO6nBUnUnbsycOHCI\n"
                       "TdSPVr6U1NlFvwfCpx7uNTXULT4cCvNpHJo2Z6cNa1Bs6+1scqawD8OzdrdcBiRo\n"
                       "s28Vv+rXnnH04r/gcyBjf5RtSA67CEPk778cwwkAajPfNIlNi5znGPNd0WH1uuoN\n"
                       "Gl+lI3K9uN7qWm9eDknVOSJlgbnk8sbx/WSk3/MCOLx2orRccI7LTTso1NAo9PjV\n"
                       "9qKWxZx8yl8h+eJ+KEYKS7NeFhV3hvnWmOVsto88lpQgTeBnROixulC0A+WYAMdo\n"
                       "s71FAoIBAB9k24zsrdGl/L5pnzqMC8PmOeustnZ9i5gZ+B/0AtNYgnoA8og3iHci\n"
                       "fyh4AgDwhYloSjR3pTui0YDCWLd/Eg4PKWT15YI+n+kiVrUeGF5KYQusyrYpl91r\n"
                       "Ws4Ji+J61dSMyjy184+tP6JHwmgYhhG5JeENQurM5FQm3vXVX1HL6KZAPeapN28n\n"
                       "PLk20+8oE54NkkMMKUSp0MvUU707FE/3Yfd65qpkB9z+foxyQXsDUkAuoeRJsIun\n"
                       "HfehWecGcsuTzkRwb23ie76caesi0Y6nwqQVHwx3pcjcU78Pj4jmJpnhAkUHjgkS\n"
                       "0x3wuH27xlijLjrk9Zockrya7ZBrRx8CggEASD7dekxw7mrbXNFdbmilJdNBFG5C\n"
                       "WlDe2kIYwn7xZoJwLqkl7NkxuwWxWuTK2BYhtKY4xb3LqY7X/3ecRsYEPbygqKGQ\n"
                       "XsVg2fz1aHLNNvmcq9Db1TbGfBbDhrpvQZxcVjqbWix8J5EsX1peza1M4Gc7DBH7\n"
                       "4KWY21AOuG5rWU//3G8DEdrML6qvcp0jqKZbGbQF98eW6Am/EbhTMJljAGoSmZX1\n"
                       "ZVROG4yjlzCj5jCYH10JfvWXsS/qGtXBEG4+Ex2g1ghyYKG5vnQabm+B0R3143rf\n"
                       "CHMEXSyY0ogXeNBv78td7X/+pf8j68Yuze9nzldPRL7/fuZ3Yu//NGfTgA==\n"
                       "-----END RSA PRIVATE KEY-----\n",
            "public": "-----BEGIN PUBLIC KEY-----\n"
                      "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAup8gRjJMk4c4vFcu8qYw\n"
                      "njReK13rgqDELvHbSDyuxbJL9koVc9OGl6oETw1mbIKTsPNZOgfDJTOzHxCjmiLw\n"
                      "We9JlO3T7jfJpvifQIHbfZ7yXJbePTpE+RkzWETQXSBbC8TUCe4w0JcWAD5qKUxl\n"
                      "ab7akfJmrQDR2QYEUOFPAyi/l1UMRtbJ4tyHQ7J8PREXeAp2I5TjlbTpEtsy2Y7B\n"
                      "DfgBr30NSjSvn43nJw6+0dMudvlF3i4MQLIhLfcTU7XLg7K2ZB0hovRgq7Bnx45K\n"
                      "gruDIw18T2yVVJBAPHsyusCcGRdGQnZzDKlhaJiUc/5UHkN2UDB3zVVZNzm2WCJh\n"
                      "eoN61VHtVGLjf45On/kggSHScMIT4yCTwKL0VhEFf/vwSYwXC7Ft6TtWUGrl5G76\n"
                      "+oWEXaTFDTLddu8EAln7Mu6r09dqFqhsd4MJBlPWTlOErGrIy3xeb/rKgFxmVdnJ\n"
                      "GynvYvZYDkks8f4M8nxBp0InRrjm7KzwSewy0p+xMLa5UzrZkjl/xF0Sby48uSGn\n"
                      "VdnFNEvPjBSwHMuJl3Btg+i9zi4YGMaNMm8otJTX0Hgrso5GyI7moqm8O0g1NhiG\n"
                      "w2iF3fZW9Z8uoe8/Z0KebmeoUKw0dKoxoEHRp2XWeMTcRM+uQCVJrNv8RqbPTyno\n"
                      "WoqonFyTWehJ3IZg/Nw2b5cCAwEAAQ==\n"
                      "-----END PUBLIC KEY-----\n",
        }

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
        client.credentials()

        pre_signup_data = self._make_pre_signup_data(nickname)

        res = client.get(reverse("user-me"))

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
        super().setUp()
        self.user, self.client = self.signup_user(**kwargs)
        self.no_signup_client = APIClient()

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