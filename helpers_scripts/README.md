## generate_fake_db.py
generate fake database and store it to files

### Entities schema
**id**: string  
**type_id**: string  
**score**: float  
**geolocation**: geojson  
**offset**: integer  
**length**: integer  
**doc_id**: string  

#### details:
id: unique identifier  
type_id: foreign key to item in finite type list  
score: nlp score for the extracted entity, in range of [0-100]  
geolocation: in case of LOCATION entity, it has geographic location  
offset: offset in original doc text where entity text starts  
length: length of the entity text  
doc_id: foreign key to doc  

### Documents schema
**id**: string  
**text**: string  

#### details
id: unique identifier  
text: text of the document  

### List schema
**id**: string  
**list_name**: string
**sub_list_value**: string

#### details  
id: unique identifier  
list_name: name of the type of list  
sub_list_value: actual sub type value  

**example**  

1, ENTITY_TYPE, LOCATION, null,  
2, ENTITY_TYPE, LOCATION, RESTAURANT  
3, ENTITY_TYPE, LOCATION, HOTEL  
4, ENTITY_TYPE, PERSON, null  
5, ENTITY_TYPE, PERSON, MANAGER  
...  
...  

**notes**  
In case that sub_list isn't relevant, then all column is null  