"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'users/', include('users.urls')),
    path(r'auth/', obtain_auth_token),
    path(r'graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))) # GraphQLView 클래스에 dispatch 함수가 ensure_csrf_cookie 데코레이터를 통해 CSRF 토큰을 강제하고 있기 때문에 이를 우회하기 위한 방법이다.
]

