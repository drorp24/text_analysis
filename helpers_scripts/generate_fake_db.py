from typing import Dict, List, Optional, Tuple, Union
from faker import Faker
import random
from random import randrange, shuffle
import json
import uuid
import fnc

# *************** CONSTANTS AND INITIALIZATIONS ***************
DOC_COUNT = 100
MIN_ENTITIES_PER_DOC = 2
MAX_ENTITIES_PER_DOC = 20
MAX_SCORE = 100
MIN_SCORE = 0
TEXT_LOCALIZATION = 'he_IL' # ar_AA

LISTS = {
    'ENTITY_TYPE': ['LOCATION', 'PERSON', 'DEVICE'],
    'PERSON_SUB_TYPE': ['MANAGER', 'EMPLOYEE', 'DIRECTOR'],
    'LOCATION_SUB_TYPE': ['HOTEL', 'WAREHOUSE', 'APARTMENT', 'HOSPITAL'],
    'DEVICE_SUB_TYPE': ['PHONE', 'IPAD'],
    'PERSON_LOCATION_RELATION': ['OWNS', 'LIVES_IN', 'MANAGE'],
    'DEVICE_LOCATION_RELATION': ['FOUND_AT'],
    'PERSON_DEVICE_RELATION': ['OWNS', 'USE']
}

fake = Faker(TEXT_LOCALIZATION)


# *************** HELPER CLASSES ******************************


class ListItemType:
    def __init__(self, _id: str, list_name: str, value: Optional[str]):
        self.id = _id
        self.list_name = list_name
        self.value = value


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
    def __init__(self, _id: str, doc_id: str, entity_type_id: str, entity_sub_type_id: Optional[str], score: float, geolocation: str, text_info: TextInfo):
        self.id = _id
        self.doc_id = doc_id
        self.type_id = entity_type_id
        self.sub_type_id = entity_sub_type_id
        self.score = score
        self.geolocation = geolocation
        self.offset = text_info.offset
        self.length = text_info.length
        self.word = text_info.word

    def __str__(self):
        return f"************************\nid: {self.id}, doc_id: {self.doc_id}, type_id: {self.type_id}, sub_type_id: {self.sub_type_id}, \n score: {self.score}, offset: {self.offset}, length: {self.length},\n geolocation: {self.geolocation}, word: {self.word}"

class Relation:
    def __init__(self, _id: str, from_entity_id: str, to_entity_id: str, list_item_id: str):
        self.id = _id
        self.from_entity_id = from_entity_id
        self.to_entity_id = to_entity_id
        self.list_item_id = list_item_id

# *************** LOGIC *********************************************

class DocEntitiesGenerator:
    def __init__(self):
        self.lists: List[ListItemType] = []
        self.docs: List[Document] = []
        self.entities: List[Entity] = []

    def generate(self):
        self.lists: List[ListItemType] = self._generate_lists()
        self.docs: List[Document] = self._generate_docs()
        self.entities: List[Entity] = self._generate_entities()
        self.relations: List[Relation] = self._generate_relations()


    @staticmethod
    def get_fake_localized_geo_point():
        random_lat = 31 + random.random() * 2
        random_lon = 34 + random.random() * 2
        return (random_lat, random_lon)

    @staticmethod
    def cast_to_postgis_geography(point_or_polygon):
        casted_geo: str = ""
        if isinstance(point_or_polygon, tuple):
            casted_geo = f"POINT({point_or_polygon[1]} {point_or_polygon[0]})"  # TODO check lat long order
        else:
            list_to_flat = point_or_polygon['geometry']['coordinates'][0]
            flat_list = [val for sublist in list_to_flat for val in sublist]
            poly_as_couples = []
            for idx in range(0, len(flat_list), 2):
                poly_as_couples.append(f"{flat_list[idx]} {flat_list[idx + 1]}")
            casted_geo = f"POLYGON(({','.join(poly_as_couples)}))"  # TODO check lat long order
        return casted_geo

    def _get_random_list_item(self, list_name: str, nullable: bool = False) -> ListItemType:
        relevant_list: List[ListItemType] = [listItem for listItem in self.lists if listItem.list_name == list_name]
        if nullable: relevant_list.append(None)
        return relevant_list[randrange(start=0, stop=len(relevant_list))]

    def _get_entities_from_document(self, document: Document, geographic_polygons: List[Dict]) -> List[Entity]:
        doc_words_shuffled = document.text.split(" ")
        shuffle(doc_words_shuffled)
        doc_entities = []
        entities_count = randrange(start=0, stop=MAX_ENTITIES_PER_DOC + 1)
        for idx, word in enumerate(doc_words_shuffled[:entities_count]):
            entity_type: ListItemType = self._get_random_list_item(list_name='ENTITY_TYPE')
            entity_sub_type: Optional[ListItemType] = self._get_random_list_item(list_name=f"{entity_type.value}_SUB_TYPE", nullable=True)
            entity_sub_type_id = entity_sub_type.id if entity_sub_type is not None else None
            random_true_false = random.random() > 0.5
            random_geo: Union[Tuple[str], Dict] = \
                DocEntitiesGenerator.get_fake_localized_geo_point() if random_true_false else \
                    geographic_polygons[randrange(start=0, stop=len(geographic_polygons))]
            text_location = TextInfo(offset=document.text.index(word), length=len(word), word=word)
            entity = Entity(_id=str(uuid.uuid4()), doc_id=document.id, entity_type_id=entity_type.id, entity_sub_type_id=entity_sub_type_id,
                            score=randrange(start=0, stop=MAX_SCORE + 1), geolocation=DocEntitiesGenerator.cast_to_postgis_geography(random_geo), text_info=text_location)
            doc_entities.append(entity)

        return doc_entities

    def _generate_entities(self) -> List[Entity]:
        entities_all_docs: List[Entity] = []
        with open(f'../data/buildings_poly_in_haifa.json') as json_file:
            _geographic_polygons = json.load(json_file)
        for doc in self.docs:
            doc_entities: List[Entity] = self._get_entities_from_document(document=doc, geographic_polygons=_geographic_polygons)
            entities_all_docs.extend(doc_entities)
        return entities_all_docs


    def _generate_relations(self) -> List[Relation]:
        relations_count = round((MIN_ENTITIES_PER_DOC + MAX_ENTITIES_PER_DOC) / 2 * DOC_COUNT)
        lists_by_id = fnc.keyby("id", self.lists)
        valid_from_to_ids = [('PERSON_SUB_TYPE','DEVICE_SUB_TYPE'),('PERSON_SUB_TYPE','LOCATION_SUB_TYPE'),
                             ('DEVICE_SUB_TYPE','LOCATION_SUB_TYPE')]
        relations = []
        while relations_count:
            from_entity = self.entities[randrange(start=0, stop=len(self.entities))]
            to_entity = self.entities[randrange(start=0, stop=len(self.entities))]
            if from_entity.sub_type_id is None or to_entity.sub_type_id is None: continue
            if (lists_by_id[from_entity.sub_type_id].list_name, lists_by_id[to_entity.sub_type_id].list_name) in valid_from_to_ids:
                from_ent_type = lists_by_id[from_entity.sub_type_id].list_name.split('_')[0]
                to_ent_type = lists_by_id[to_entity.sub_type_id].list_name.split('_')[0]
                possible_relation_list_name = f"{from_ent_type}_{to_ent_type}_RELATION"
                if possible_relation_list_name not in LISTS: continue
                possible_relations_ids = [item.id for item in self.lists if item.value in LISTS[possible_relation_list_name]]
                relation = Relation(_id=str(uuid.uuid4()), from_entity_id=from_entity.id, to_entity_id=to_entity.id,
                                    list_item_id=possible_relations_ids[randrange(start=0, stop=len(possible_relations_ids))])
                relations.append(relation)
            relations_count -= 1
        return relations

    def _generate_lists(self) -> List[ListItemType]:
        list_items = []
        for idx, (key, list_) in enumerate(LISTS.items()):
            for inner_idx, value in enumerate(list_):
                list_items.append(ListItemType(_id=f"{idx}_{inner_idx}", list_name=key, value=value))
        return list_items

    @staticmethod
    def _generate_docs() -> List[Document]:
        docs = [Document(_id=f"doc_{idx}", text="/n".join(fake.paragraphs())) for idx in range(DOC_COUNT)]
        return docs

    def store_to_json_files(self, dir_path="../data"):
        lists_to_dump = [
            {"file_name": "lists.json", "items": self.lists},
            {"file_name": "documents.json", "items": self.docs},
            {"file_name": "entities.json", "items": self.entities},
            {"file_name": "relations.json", "items": self.relations}
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
