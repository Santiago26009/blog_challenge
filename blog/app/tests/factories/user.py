import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: "user_{}@example.com".format(n))
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = "username"
    password = "password"

    class Meta:
        model = get_user_model()
