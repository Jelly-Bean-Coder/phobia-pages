import json

def parse_files():
    with open('./static/json/phobias.json') as f: # Fears parser
        fears = json.load(f)

        from .extensions import db
        from .models import Phobia, Tag


        for fear in fears:
            current_phobia = Phobia(
                name=fear.get('name'),
                definition=fear.get('definition'),
                summary=fear.get('summary'),
                description=fear.get('description'),
                symptoms=fear.get('symptom'),
            )
            db.session.add(current_phobia)

    tags = []
    with open('./static/json/tags.json') as f:
        tags_data = json.load(f)
        for tag_category in tags_data:
            for tag in tags_data[tag_category]:
                tags.append(Tag(name=tag))

    db.session.add_all(tags)
    db.session.commit()
