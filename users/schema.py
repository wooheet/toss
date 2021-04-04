import graphene
from graphene import relay, ObjectType, InputObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from users.models import User
from config import utils
from datetime import datetime


# class CreateUserAttribute:
#     email = graphene.String(required=True)
#     username = graphene.String(required=True)
#     password = graphene.String(required=True)
#     first_name = graphene.String(required=False)
#     last_name = graphene.String(required=False)
#     is_staff = graphene.Boolean(required=False)
#     is_active = graphene.Boolean(required=False)
#
#
# class UserNode(DjangoObjectType):
#     """User node."""
#
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
# class CreateUserInput(graphene.InputObjectType, CreateUserAttribute):
#     """Arguments to create a user."""
#     pass
#
#
# class CreateUser(graphene.Mutation):
#     """Create a planet."""
#     user = graphene.Field(lambda: UserNode,
#                           description="User created by this mutation.")
#
#     class Arguments:
#         input = CreateUserInput(required=True)
#
#     def mutate(self, info, input):
#         data = utils.input_to_dictionary(input)
#         data['created'] = datetime.utcnow()
#
#         user = User.objects.create_user(**data)
#         user.save()
#
#         return CreateUser(user=user)
#
#
# class Query(ObjectType):
#     users = relay.Node.Field(UserNode)  # get user by id or by field name
#     all_users = DjangoFilterConnectionField(UserNode)  # get all users
#
#     def resolve_users(self):
#         return User.objects.all()


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


class Mutation(ObjectType):
    create_user = CreateUser.Field()
