import pymorphy2

from location_extractor.extractor import BasePipeline
from location_extractor.lang import Lang
from location_extractor.location import LocationsCollection


class UkPipeline(BasePipeline):
    _lang = Lang.UK

    def __init__(self, locations: LocationsCollection, use_gpu: bool = False):
        super().__init__(locations, use_gpu)

        self.moph_analyzer = pymorphy2.MorphAnalyzer(lang='uk')
        self.custom_lemmatizer = {}

    def _lemmatize(self, entities, text):
        not_lemmas = list(map(lambda x: x.lower(), entities))
        lemmas = []
        for loc in entities:
            parts = []
            for token in loc.split():
                lemma = self.moph_analyzer.parse(token)[-1].normal_form
                if lemma in self.custom_lemmatizer:
                    lemma = self.custom_lemmatizer[lemma]
                parts.append(lemma)
            lemmas.append(' '.join(parts))

        for i, lemma in enumerate(lemmas):
            if lemma.endswith("обл"):
                lemma = lemma.replace("обл", "область")

            lemmas[i] = lemma.replace("ий обл", "а обл")

        return list(set(not_lemmas)), list(set(lemmas))
