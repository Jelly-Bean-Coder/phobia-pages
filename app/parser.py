import json

def parse_files():
    with open('./static/json/phobias.json') as f: # Fears parser
        fears = json.load(f)

        names, types, definitions, summaries, descriptions, symptoms=[],[],[],[],[],[]


        for fear in fears:
           names.append(fear["name"]) # Get all names
           types.append(fear["type"])
           definitions.append(fear["definition"])
           summaries.append(fear["summary"])
           descriptions.append(fear["description"])
           symptoms.append(fear["symptoms"])

    from . import cursor
    from .models import Phobia, Tag

    for fear_index, fear in enumerate(fears): # Fears adder
        Phobia(
            name = names[fear_index],
            definition = definitions[fear_index],
            summary = summaries[fear_index],
            description = descriptions[fear_index],
            symptoms= symptoms[fear_index]
            )
        cursor.add_all()
        cursor.commit()



    with open('tags.json') as f:
        global tags

        tags_data = json.load(f)
        for tag_category in tags_data:
            for tag in tags_data[tag_category]:
                tags.append(tag)


    tag_object_list = [Tag(name=tag) for tag in tags]

    cursor.add_all(tag_object_list)
    cursor.commit()
