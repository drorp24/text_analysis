from typing import Dict, List, Optional, Tuple
from faker import Faker
from random import randrange, shuffle
import json
import uuid

# *************** CONSTANTS AND INITIALIZATIONS ***************
DOC_COUNT = 100
MIN_ENTITIES_PER_DOC = 2
MAX_ENTITIES_PER_DOC = 20
MAX_SCORE = 100
MIN_SCORE = 0
TEXT_LOCALIZATION = 'ar_AA'  # Saudi Arabian Arabic
GEO_LOCALIZATION = 'IL'  # Israel

ENTITY_TYPES = {
    'LOCATION': [None, 'HOTEL', 'WAREHOUSE', 'APARTMENT', 'HOSPITAL'],
    'PERSON': [None, 'MANAGER', 'EMPLOYEE', 'DIRECTOR']
}

fake = Faker(TEXT_LOCALIZATION)


# *************** HELPER CLASSES ******************************


class EntityType:
    def __init__(self, _id: str, list_name: str, sub_list_name: Optional[str]):
        self.id = _id
        self.list_name = list_name
        self.sub_list_name = sub_list_name

    def get_full_id(self):
        has_sub_list = self.sub_list_name is not None
        return f"{self.list_name}_{self.sub_list_name}" if has_sub_list else f"{self.list_name}"


class Document:
    def __init__(self, _id: str, text: str):
        self.id = _id
        self.text = text


class TextInfo:
    def __init__(self, offset: int, length: int, word: str):
        self.offset = offset
        self.length = length
        self.word = word


class Entity:
    def __init__(self, _id: str, doc_id: str, entity_type: EntityType, score: float, geolocation: str, textInfo: TextInfo):
        self.id = _id
        self.doc_id = doc_id
        self.type_id = entity_type.list_name
        self.sub_type_id = entity_type.sub_list_name
        self.score = score
        self.geolocation = geolocation
        self.offset = textInfo.offset
        self.length = textInfo.length
        self.word = textInfo.word

    def __str__(self):
        return f"************************\nid: {self.id}, doc_id: {self.doc_id}, type_id: {self.type_id}, sub_type_id: {self.sub_type_id}, \n score: {self.score}, offset: {self.offset}, length: {self.length},\n geolocation: {self.geolocation}, word: {self.word}"


# *************** LOGIC *********************************************

class DocEntitiesGenerator:
    def __init__(self):
        self.entity_types: List[EntityType] = None
        self.docs: List[Document] = None
        self.entities: List[EntityType] = None

    def generate(self):
        self.entity_types: List[EntityType] = self._generate_entity_type_list()
        self.docs: List[Document] = self._generate_docs()
        self.entities: List[EntityType] = self._generate_entities()

    def _get_random_entity_type(self) -> EntityType:
        entity_types_len = len(self.entity_types)
        return self.entity_types[randrange(start=0, stop=entity_types_len)]

    def _get_entities_from_document(self, document: Document) -> List[EntityType]:
        entities_count = randrange(start=0, stop=MAX_ENTITIES_PER_DOC + 1)
        doc_words_shuffled = document.text.split(" ")
        shuffle(doc_words_shuffled)
        doc_entities = []
        for idx, word in enumerate(doc_words_shuffled[:entities_count]):
            entity_type: EntityType = self._get_random_entity_type()
            random_geo: Tuple[str] = fake.local_latlng(country_code=GEO_LOCALIZATION, coords_only=True)
            textLocation = TextInfo(offset=document.text.index(word), length=len(word), word=word)
            entity = Entity(_id=str(uuid.uuid4()), doc_id=document.id, entity_type=entity_type,
                            score=randrange(start=0, stop=MAX_SCORE + 1), geolocation=json.dumps(random_geo), textInfo=textLocation)
            doc_entities.append(entity)

        return doc_entities

    def _generate_entities(self) -> List[EntityType]:
        paragraphs: List[str] = fake.paragraphs()
        entities_all_docs: List[EntityType] = []
        for doc in self.docs:
            doc_entities: List[EntityType] = self._get_entities_from_document(document=doc)
            entities_all_docs.extend(doc_entities)
        return entities_all_docs

    def _generate_entity_type_list(self):
        entity_types_keys: List[str] = [key for key in ENTITY_TYPES.keys()]
        entity_types = []
        for ext_idx, entity_type_key in enumerate(entity_types_keys):
            sub_type_list = ENTITY_TYPES[entity_type_key]
            for int_idx, entity_sub_type_key in enumerate(sub_type_list):
                entity_types.append(EntityType(_id=f"{ext_idx}_{int_idx}", list_name=entity_type_key, sub_list_name=entity_sub_type_key))
        return entity_types

    @staticmethod
    def _generate_docs() -> List[Document]:
        paragraphs = fake.paragraphs()
        docs = [Document(_id=f"doc_{idx}", text="/n".join(paragraphs)) for idx in range(DOC_COUNT)]
        return docs

    def store_to_json_files(self, dir_path="../data"):
        lists_to_dump = [
            {"file_name": "entity_type.json", "items": self.entity_types},
            {"file_name":"documents.json", "items": self.docs},
            {"file_name":"entities.json", "items": self.entities}
        ]
        for item in lists_to_dump:
            with open(f"{dir_path}/{item['file_name']}", "w") as f:
                items_as_string: str = "\n,".join([json.dumps(entity.__dict__) for entity in item['items']])
                f.write(f"[{items_as_string}]")

    def print(self):
        for entity in self.entities:
            print(entity)
        print(f"{len(self.entities)} entities from {len(self.docs)} documents")

if __name__ == '__main__':
    docEntitiesGenerator = DocEntitiesGenerator()
    docEntitiesGenerator.generate()
    docEntitiesGenerator.store_to_json_files()