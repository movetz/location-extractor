import os
from unittest import TestCase

from location_extractor.location import CsvCollection
from location_extractor.pipelines.ru_pipeline import RuPipeline


class TestRuPipeline(TestCase):

    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        collection = CsvCollection(
            locations_path=f"{dir_path}/../../location_extractor/files/locations.csv",
            regions_path=f"{dir_path}/../../location_extractor/files/regions.csv",
        )

        cls.pipeline = RuPipeline(
            locations=collection,
        )

    def test_extract_locations_from_text(self):

        location_variants = {
            "Артемовск переименовали в Бахмут, а Кировоград в Кропивницкий.": ["Бахмут", "Кропивницкий"],
            "По Харькову был нанесен удар С-300.": ["Харьков"],
            "Из Киева в Борисполь начал курсировать поезд.": ["Киев", "Борисполь"],
            "Владимир Зеленский посетил Киевский район Донецка": ["Донецк"],
        }

        for text, target_names in location_variants.items():
            regions, locations = self.pipeline.extract_locations_from_text(text)

            location_names = [location.name_ru for location in locations]

            self.assertEqual(sorted(target_names), sorted(location_names))

        region_variants = {
            "Власти Крыма сообщили о приостановке движения поездов на перегоне Симферополь — Севастополь": ["Крым"],
            "Владимир Зеленский посетил Сумскую область": ["Сумская область"],
            "Владимир Зеленский посетил Сумскую обл.": ["Сумская область"],
        }

        for text, target_names in region_variants.items():
            regions, locations = self.pipeline.extract_locations_from_text(text)

            region_names = [region.name_ru for region in regions]

            self.assertEqual(sorted(target_names), sorted(region_names))
