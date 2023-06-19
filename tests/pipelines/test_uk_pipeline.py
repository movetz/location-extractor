import os
from unittest import TestCase

from location_extractor.location import CsvCollection
from location_extractor.pipelines.uk_pipeline import UkPipeline


class TestUkPipeline(TestCase):

    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        collection = CsvCollection(
            locations_path=f"{dir_path}/../../location_extractor/files/locations.csv",
            regions_path=f"{dir_path}/../../location_extractor/files/regions.csv",
        )

        cls.pipeline = UkPipeline(
            locations=collection,
        )

    def test_extract_locations_from_text(self):
        location_variants = {
            "Артемівськ перейменували в Бахмут, а Кіровоград в Кропивницький.": ["Бахмут", "Кропивницький"],
            "СБУ ліквідувала у Дніпрі наркоугруповання, яке діяло «під дахом» місцевих правоохоронців.": ["Дніпро"],
            "Володимир Зеленський відвідав місто Донецьк": ["Донецьк"],
        }

        for text, target_names in location_variants.items():
            regions, locations = self.pipeline.extract_locations_from_text(text)

            location_names = [location.name_uk for location in locations]

            self.assertEqual(sorted(target_names), sorted(location_names))

        region_variants = {
            "Запорізька область – зафіксовано рух БпЛА Shahed": ["Запорізька область"],
            "Володимир Зеленський відвідав місто Тростянець Сумської області": ["Сумська область"],
            "Володимир Зеленський відвідав місто Тростянець Сумської обл.": ["Сумська область"],
            "Володимир Зеленський відвідав Луганщину": ["Луганська область"],
        }

        for text, target_names in region_variants.items():
            regions, locations = self.pipeline.extract_locations_from_text(text)

            region_names = [region.name_uk for region in regions]

            self.assertEqual(sorted(target_names), sorted(region_names))
