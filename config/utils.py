from enum import Enum
from graphql_relay.node.node import from_global_id


def input_to_dictionary(input):
    """Method to convert Graphene inputs into dictionary."""
    dictionary = {}
    for key in input:
        # Convert GraphQL global id to database id
        if key[-2:] == 'id' and input[key] != 'unknown':
            input[key] = from_global_id(input[key])[1]
        dictionary[key] = input[key]
    return dictionary


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def get_values(cls):
        return[x.value for x in cls]

    @classmethod
    def get_keys(cls):
        return [x.name for x in cls]