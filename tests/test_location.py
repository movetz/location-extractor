from unittest import TestCase
import os

from location_extractor.lang import Lang
from location_extractor.location import CsvCollection


class TestCsvCollection(TestCase):
    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        cls.collection = CsvCollection(
            locations_path=f"{dir_path}/../location_extractor/files/locations.csv",
            regions_path=f"{dir_path}/../location_extractor/files/regions.csv",
        )

    def test_get_norm_names(self):
        collection = self.collection

        self.assertTrue(collection.check_location_by_norm_name("днепр", Lang.RU))
        self.assertTrue(collection.check_location_by_norm_name("днепропетровск", Lang.RU))
        self.assertTrue(collection.check_location_by_norm_name("дніпро", Lang.UK))
        self.assertTrue(collection.check_location_by_norm_name("дніпропетровськ", Lang.UK))

        self.assertFalse(collection.check_location_by_norm_name("йофиооги", Lang.RU))
        self.assertFalse(collection.check_location_by_norm_name("йофиооги", Lang.UK))

        norm_names_ru = collection.get_norm_names(Lang.RU)

        self.assertIn("днепр", norm_names_ru)
        self.assertIn("днепропетровск", norm_names_ru)

        norm_names_uk = collection.get_norm_names(Lang.UK)

        self.assertIn("дніпро", norm_names_uk)
        self.assertIn("дніпропетровськ", norm_names_uk)

        location_first = collection.get_locations_by_norm_name("днепр", Lang.RU)[0]

        location_second = collection.get_locations_by_norm_name("днепропетровск", Lang.RU)[0]
        self.assertEqual(location_first, location_second)

        location_second = collection.get_locations_by_norm_name("дніпро", Lang.UK)[0]
        self.assertEqual(location_first, location_second)

        location_second = collection.get_locations_by_norm_name("дніпропетровськ", Lang.UK)[0]
        self.assertEqual(location_first, location_second)

        multiple_locations_first = collection.get_locations_by_norm_name("макіївка", Lang.UK)
        self.assertEqual(len(multiple_locations_first), 8)

    def test_get_region_by_norm_name(self):
        collection = self.collection

        region_first = collection.get_region_by_norm_name("луганская область", Lang.RU)

        region_second = collection.get_region_by_norm_name("луганська область", Lang.UK)
        self.assertEqual(region_first, region_second)

        region_second = collection.get_region_by_norm_name("лнр", Lang.RU)
        self.assertEqual(region_first, region_second)

        region_second = collection.get_region_by_norm_name("луганщина", Lang.UK)
        self.assertEqual(region_first, region_second)

        self.assertTrue(True)
