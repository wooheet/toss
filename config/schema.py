import graphene
from users.schema import Query as UserQuery


class Query(UserQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)