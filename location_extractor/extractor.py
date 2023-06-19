from abc import ABC, abstractmethod
from string import punctuation
from typing import List

import pandas as pd
import stanza
from rapidfuzz import fuzz, process

from location_extractor.lang import Lang
from location_extractor.location import Location, LocationsCollection, Region


class LocationExtractor:

    def extract_locations_from_text(self, text: str, lang: str) -> tuple[Location]:
        pass


class BasePipeline(ABC):
    _lang: Lang = None

    def __init__(self, locations: LocationsCollection, use_gpu: bool = False):
        self._locations = locations
        self._ner_model = stanza.Pipeline(lang=self._lang.value, processors="tokenize,ner,lemma", use_gpu=use_gpu)

    def extract_locations_from_text(self, text: str) -> tuple[List[Region], List[Location]]:
        preprocessed = self._preprocess(text)
        entities = self._extract_entities(preprocessed)
        not_lemmas, lemmas = self._lemmatize(entities, text)
        regions = self._match_regions(lemmas, not_lemmas)
        locations = self._match_locations(lemmas, not_lemmas)

        return regions, locations

    def _preprocess(self, text) -> str:
        _punctuation = punctuation + '–'

        text = text.replace('**', ' ')
        text = "".join([s for s in text if (s.isalnum()) or s == ' ' or s in _punctuation or s == '\n'])
        text = text.encode('utf-8', 'ignore').decode("utf-8")
        text = text.replace('\n', ' ')
        text = ' '.join(text.split())

        return text

    def _extract_entities(self, text) -> List[str]:
        entities = list(map(lambda x: (x.to_dict()['text'], x.to_dict()['type']), self._ner_model(text).entities))
        loc_entities = list(map(lambda x: x[0], filter(lambda x: x[1] in ['LOC', 'MISC'], entities)))
        loc_entities = [''.join([s for s in word if s.isalpha() or s in [' ', '-', 'ʼ']]) for word in loc_entities]
        return loc_entities

    @abstractmethod
    def _lemmatize(self, entities, text):
        pass

    def _match_regions(self, lemmas: List[str], not_lemmas: List[str]) -> List[Region]:
        regions = {}
        not_lemmas.extend(lemmas)
        entities = set(not_lemmas)

        for entity in entities:
            region = self._locations.get_region_by_norm_name(entity, self._lang)

            if region and region.id not in regions:
                regions[region.id] = region

        return list(regions.values())

    def _match_locations(self, lemmas: List[str], not_lemmas: List[str]) -> List[Location]:
        locations = {}
        not_lemmas.extend(lemmas)
        entities = set(not_lemmas)

        for entity in entities:
            matched_locations = self._locations.get_locations_by_norm_name(entity, self._lang)

            if len(matched_locations) > 0:
                for matched_location in matched_locations:
                    if matched_location.id not in locations:
                        locations[matched_location.id] = matched_location

                continue

            if not pd.isna(entity):
                res = process.extract(entity, self._locations.get_norm_names(self._lang), scorer=fuzz.ratio,
                                      score_cutoff=96, limit=30)
                if len(res) > 0:
                    for res_item in res:
                        matched_locations = self._locations.get_locations_by_norm_name(res_item[0], self._lang)
                        for matched_location in matched_locations:
                            if matched_location.id not in locations:
                                locations[matched_location.id] = matched_location

        return list(locations.values())
