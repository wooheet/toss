# import graphene
# from graphene_django.types import DjangoObjectType
#
# from .models import User
# from graphql import GraphQLError
#
#
# class UserType(DjangoObjectType):
#     class Meta:
#         model = User
#
#
# class Query(object):
#     user = graphene.Field(UserType, email=graphene.String())
#
#     def resolve_user(self, info, **kwargs):
#         email = kwargs.get('email')
#         return User.objects.filter(email=email).first()
#
#
# class CreateUser(graphene.Mutation):
#     class Arguments:
#         # The input arguments for this mutation
#         email = graphene.String()
#
#     # The class attributes define the response of the mutation
#     user = graphene.Field(UserType)
#
#     @classmethod
#     def mutate(cls, root, info, email):
#         user = User(
#             email=email,
#         )
#         user.save()
#
#         return CreateUser(
#             email=user.email,
#         )
#
#
# class Mutation(graphene.ObjectType):
#     create_user = CreateUser.Field()
import graphene

from graphene import relay, ObjectType, InputObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.core.exceptions import ValidationError
from users.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class CreateUser(graphene.Mutation):
    email = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)

    def mutate(self, info, username, email):
        print('email', email)
        user = User.objects.create_user(
            username=username,
            email=email,
        )
        user.set_password('password')
        user.save()

        return CreateUser(email=email)


class Query(object):
    user = graphene.Field(UserType, email=graphene.String())

    def resolve_user(self, info, **kwargs):
        email = kwargs.get('email')
        print(User.objects.filter(email=email).first())
        return User.objects.filter(email=email).first()


# class UserCreateInput(InputObjectType):
#     username = graphene.String(required=True)
#     first_name = graphene.String(required=False)
#     last_name = graphene.String(required=False)
#     email = graphene.String(required=True)
#     is_staff = graphene.Boolean(required=False)
#     is_active = graphene.Boolean(required=False)
#     password = graphene.String(required=True)
#
#
# class UserNode(DjangoObjectType):
#     class Meta:
#         model = User
#         # Allow for some more advanced filtering here
#         filter_fields = {
#             'first_name': ['exact', 'icontains', 'istartswith'],
#             'last_name': ['exact', 'icontains', 'istartswith'],
#             'username': ['exact'],
#         }
#         interfaces = (relay.Node,)
#
#
# class CreateUser(relay.ClientIDMutation):
#     class Input:
#         user = graphene.Argument(UserCreateInput)
#
#     new_user = graphene.Field(UserNode)
#
#     @classmethod
#     def mutate_and_get_payload(cls, args, context, info):
#         user_data = args.get('user')
#
#         # unpack the dict item into the model instance
#         new_user = User.objects.create(**user_data)
#         new_user.set_password(user_data.get('password'))
#         new_user.save()
#
#         return cls(new_user=new_user)


# class Query(ObjectType):
#     users = relay.Node.Field(UserNode)  # get user by id or by field name
#     all_users = DjangoFilterConnectionField(UserNode)  # get all users
#
#     def resolve_users(self):
#         return User.objects.all()


class Mutation(ObjectType):
    create_user = CreateUser.Field()