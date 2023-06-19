from _csv import reader
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List

from location_extractor.lang import Lang


@dataclass
class Region:
    id: int
    name_uk: str
    name_ru: str
    country: str
    priority: int
    aliases_uk: List[str]
    aliases_ru: List[str]


@dataclass
class Location:
    id: int
    name_uk: str
    name_ru: str
    aliases_uk: List[str]
    aliases_ru: List[str]
    lat: float
    lon: float
    region: Region


class LocationsCollection(ABC):

    @abstractmethod
    def get_region_by_norm_name(self, norm_name: str, lang: Lang) -> Optional[Region]:
        pass

    @abstractmethod
    def get_norm_names(self, lang: Lang) -> List[str]:
        pass

    @abstractmethod
    def get_locations_by_norm_name(self, norm_name: str, lang: Lang) -> List[Location]:
        pass

    def check_location_by_norm_name(self, norm_name: str, lang: Lang) -> bool:
        pass


class CsvCollection(LocationsCollection):
    def __init__(self, locations_path: str, regions_path: str):
        self.regions = {}
        self.norm_regions_uk = {}
        self.norm_regions_ru = {}
        self.load_regions_file(regions_path)

        self.locations = {}
        self.norm_locations_uk = {}
        self.norm_locations_ru = {}
        self.load_locations_file(locations_path)

    def load_regions_file(self, regions_path: str):
        with open(regions_path, "r") as read_obj:
            csv_reader = reader(read_obj)

            for row in csv_reader:
                region = self._parse_region_row(row)
                self.regions[region.id] = region
                self._add_norm_region(region, Lang.UK)
                self._add_norm_region(region, Lang.RU)

    def _parse_region_row(self, row: List) -> Region:
        return Region(
            id=int(row[0]),
            name_uk=row[1],
            name_ru=row[2],
            country=row[3],
            priority=int(row[4]),
            aliases_uk=row[7].split(";"),
            aliases_ru=row[8].split(";"),
        )

    def _add_norm_region(self, region_obj: Region, lang: Lang) -> None:
        region_name = getattr(region_obj, "name_" + lang.value)

        region_name = region_name.lower()

        norm_regions_attr = "norm_regions_" + lang.value
        if region_name not in getattr(self, norm_regions_attr):
            getattr(self, norm_regions_attr)[region_name] = []

        getattr(self, norm_regions_attr)[region_name].append(region_obj)

        for alias in getattr(region_obj, "aliases_" + lang.value):
            alias = alias.lower()
            if alias not in getattr(self, norm_regions_attr):
                getattr(self, norm_regions_attr)[alias] = []

            getattr(self, norm_regions_attr)[alias].append(region_obj)

    def get_region_by_norm_name(self, norm_name: str, lang: Lang) -> Optional[Region]:
        if lang == lang.RU and norm_name in self.norm_regions_ru:
            return self.norm_regions_ru[norm_name][0]
        elif lang == lang.UK and norm_name in self.norm_regions_uk:
            return self.norm_regions_uk[norm_name][0]
        else:
            return None

    def load_locations_file(self, locations_path: str):
        with open(locations_path, "r") as read_obj:
            csv_reader = reader(read_obj)

            for row in csv_reader:
                loc_obj = self._parse_location_row(row)
                self.locations[loc_obj.id] = loc_obj
                self._add_norm_location(loc_obj, Lang.UK)
                self._add_norm_location(loc_obj, Lang.RU)

    def _parse_location_row(self, row: List) -> Location:
        return Location(
            id=int(row[0]),
            name_uk=row[1],
            name_ru=row[2],
            region=self.regions[int(row[3])],
            aliases_uk=row[4].split(";"),
            aliases_ru=row[5].split(";"),
            lat=row[6],
            lon=row[7],
        )

    def _add_norm_location(self, loc_obj: Location, lang: Lang) -> None:
        loc_name = getattr(loc_obj, "name_" + lang.value)

        loc_name = loc_name.lower()

        norm_locations_attr = "norm_locations_" + lang.value
        if loc_name not in getattr(self, norm_locations_attr):
            getattr(self, norm_locations_attr)[loc_name] = []

        getattr(self, norm_locations_attr)[loc_name].append(loc_obj)

        for alias in getattr(loc_obj, "aliases_" + lang.value):
            alias = alias.lower()
            if alias not in getattr(self, norm_locations_attr):
                getattr(self, norm_locations_attr)[alias] = []

            getattr(self, norm_locations_attr)[alias].append(loc_obj)

    def get_norm_names(self, lang: Lang) -> List[str]:
        if lang == lang.RU:
            return list(self.norm_locations_ru)
        elif lang == lang.UK:
            return list(self.norm_locations_uk)
        else:
            return []

    def get_locations_by_norm_name(self, norm_name: str, lang: Lang) -> List[Location]:
        if lang == lang.RU and norm_name in self.norm_locations_ru:
            return self.norm_locations_ru[norm_name]
        elif lang == lang.UK and norm_name in self.norm_locations_uk:
            return self.norm_locations_uk[norm_name]
        else:
            return []

    def check_location_by_norm_name(self, norm_name: str, lang: Lang) -> bool:
        if lang == lang.RU:
            return norm_name in self.norm_locations_ru
        elif lang == lang.UK:
            return norm_name in self.norm_locations_uk
        else:
            return False
