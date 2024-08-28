from faker import Faker

from django.core.management.base import BaseCommand

from apps.user.models import CustomUser


class Command(BaseCommand):
    help = ' Create random users and add to the custom user model'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of users to be created')


    def handle(self, *args, **kwargs):
        total = kwargs['total']
        faker = Faker()

        users_data = []
        for _ in range(total):
            username = faker.unique.user_name()[:7]  # Limiting username to 7 characters
            email = faker.unique.email()
            password = faker.password()
            address = faker.address()
            phone_number = faker.unique.msisdn()[:10]  # Limiting phone number to 10 characters

            users_data.append({
                'username': username,
                'email': email,
                'password': password,
                'address': address,
                'phone_number': phone_number,
            })

        # Create users based on the generated data
        for user_data in users_data:
            CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                address=user_data['address'],
                phone_number=user_data['phone_number']
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {total} users'))


