https://docs.djangoproject.com/en/2.2/ref/contrib/messages/ (Messages)
https://docs.djangoproject.com/en/2.2/intro/tutorial05/ (Tests)
https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/ (Pase a producción)

container_id => ?
status_id => PSQL

1. Pendiente
2. Procesado
3. Procesado con errores

```SQL
-- Traducciones para el estado 1
INSERT INTO tracking_movement_translation (original, translation) VALUES (1, 4);
INSERT INTO tracking_movement_translation (original, translation) VALUES (2, 4);
INSERT INTO tracking_movement_translation (original, translation) VALUES (3, 4);
-- Traducciones para el estado 2
INSERT INTO tracking_movement_translation (original, translation) VALUES (5, 8);
INSERT INTO tracking_movement_translation (original, translation) VALUES (6, 8);
INSERT INTO tracking_movement_translation (original, translation) VALUES (7, 8);
-- Traducciones para el estado 3
INSERT INTO tracking_movement_translation (original, translation) VALUES (9, 12);
INSERT INTO tracking_movement_translation (original, translation) VALUES (10, 12);
INSERT INTO tracking_movement_translation (original, translation) VALUES (11, 12);
-- Traducciones para el estado 4
INSERT INTO tracking_movement_translation (original, translation) VALUES (13, 15);
INSERT INTO tracking_movement_translation (original, translation) VALUES (14, 15);
```

```Python
def validate_import_value(container, data, container_attr, data_key):
    # Verificar que el valor existe
    data_value = data.get(data_key)
    if is_empty(data_value):
        return False
    # Guardar el valor en el objeto de base de datos
    setattr(container, container_attr, data_value)
    return True
```

597 ubicaciones.
4892 contenedores.
26 estados de movimientos.

He cambiado:
- "general" a "config"
- "date_formats" a "date", "time", "datetime"
- "single.processed" a "processed"
- "multiple.estimated" a "estimated"
- "single" a "container"
- "multiple" a "movements"

POSTGRES + PYTHON:
http://initd.org/psycopg/docs/usage.html#adapt-date

PASE A PRODUCCIÓN:
https://docs.aws.amazon.com/es_es/elasticbeanstalk/latest/dg/create-deploy-python-django.html

```Python
DATABASE_CARRIERS       = "tracking_enterprise"
DATABASE_CONTAINERS     = "tracking_container"
DATABASE_MOVEMENTS      = "tracking_movement"
DATABASE_CONT_STATUSES  = "tracking_container_status"
DATABASE_MOVE_STATUSES  = "tracking_movement_status"
DATABASE_LOCATIONS      = "tracking_location"

with psycopg2.connect(dbname="tracking", user="postgres", password="TODO: PASSWORD") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM tracking_container ORDER BY priority;")
        column_names = [desc[0] for desc in cur.description]
        data_rows = cur.fetchall()

def insert_or_update(self, document, collection, query_keys):
    raise Exception("TODO: TENGO QUE REESCRIBIR TODO ESTO")
    # Create shallow copy of document, with specified keys, for query
    query_document = self.create_query_document(document, query_keys)
    self.logger.info("Query document: %s", query_document)
    
    # Try to update
    if "_id" in document:
        document.pop("_id")
    document["updated_at"] = datetime.datetime.utcnow()
    result = collection.update_many(query_document, {"$set": document})
    
    if result.matched_count > 0:
        self.logger.info("Updated: %s", query_document)
        return True
    
    # If update was unsuccessful, insert document
    document["created_at"] = datetime.datetime.utcnow()
    document["updated_at"] = None
    
    result = collection.insert_one(document)
    self.logger.info("Inserted: %s", query_document)
    return True

def create_query_document(self, document, query_keys):
    query_document = {}
    for key in query_keys:
        query_document[key] = document.get(key)
    return query_document
```
