from django.core.management import call_command
from django.test import TestCase

from accounts.models import Country


class TestCountry(TestCase):

    def test_string_representation_of_the_country_instance(self):
        country_1 = Country.objects.create(country_name=None)
        country_2 = Country.objects.create(country_name='Afghanistan')

        """Checking string representation of the country instance when 'country_name' is None"""

        self.assertEqual(str(country_1), 'None')

        """Checking string representation of the country instance when 'country_name' is 'Afghanistan'"""

        self.assertEqual(str(country_2), country_2.country_name)
