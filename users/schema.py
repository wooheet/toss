import graphene
from graphene import relay, ObjectType, InputObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from users.models import User
from config import utils
from datetime import datetime


class CreateUserAttribute:
    email = graphene.String(required=True)
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    is_staff = graphene.Boolean(required=False)
    is_active = graphene.Boolean(required=False)


class UserNode(DjangoObjectType):
    """User node."""

    class Meta:
        model = User
        # Allow for some more advanced filtering here
        filter_fields = {
            'first_name': ['exact', 'icontains', 'istartswith'],
            'last_name': ['exact', 'icontains', 'istartswith'],
            'username': ['exact'],
        }
        interfaces = (relay.Node,)


class CreateUserInput(graphene.InputObjectType, CreateUserAttribute):
    """Arguments to create a user."""
    pass


class CreateUser(graphene.Mutation):
    """Create a user."""
    user = graphene.Field(lambda: UserNode,
                          description="User created by this mutation.")

    class Arguments:
        input = CreateUserInput(required=True)

    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)
        print(data)
        data['created'] = datetime.utcnow()

        user = User.objects.create_user(**data)
        user.save()

        return CreateUser(user=user)


class RequestSecret(graphene.Mutation):
    is_secret = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        print('email', email)
        try:
            User.objects.get(email=email)
            is_secret = True
        except Exception:
            is_secret = False

        return RequestSecret(is_secret=is_secret)


class Query(ObjectType):
    users = relay.Node.Field(UserNode)  # get user by id or by field name
    all_users = DjangoFilterConnectionField(UserNode)  # get all users

    def resolve_users(self):
        return User.objects.all()


class Mutation(ObjectType):
    create_user = CreateUser.Field()
    request_secret = RequestSecret.Field()
