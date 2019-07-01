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
