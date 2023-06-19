from natasha import Doc, Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger

from location_extractor.extractor import BasePipeline
from location_extractor.lang import Lang
from location_extractor.location import LocationsCollection


class RuPipeline(BasePipeline):
    _lang = Lang.RU

    def __init__(self, locations: LocationsCollection, use_gpu: bool = False):
        super().__init__(locations, use_gpu)

        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.embed = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.embed)

        self.custom_lemmatizer = {
            # "лнр": "луганский область",
            # "днр": "донецкий область",
            # "донбасс": "донецкий область",
        }

    def _lemmatize(self, entities, text):
        not_lemmas = list(map(lambda x: x.lower(), entities))
        lemmas = []
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
        lemmas_dict = {}
        for token in doc.tokens:
            lemmas_dict[token.text] = token.lemma
        for entity in entities:
            parts = []
            for part in entity.split(' '):
                if part in lemmas_dict:
                    lemma = lemmas_dict[part]
                    if lemma in self.custom_lemmatizer:
                        lemma = self.custom_lemmatizer[lemma]
                    parts.append(lemma)
            lemmas.append(' '.join(parts))

        for i, lemma in enumerate(lemmas):
            if lemma.endswith("обл"):
                lemma = lemma.replace("обл", "область")

            lemmas[i] = lemma.replace("ий обл", "ая обл")

        return list(set(not_lemmas)), list(set(lemmas))
