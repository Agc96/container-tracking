INSERT INTO tracking_enterprise (name, carrier) VALUES ('Maersk', TRUE);
INSERT INTO tracking_enterprise (name, carrier) VALUES ('Hapag-Lloyd', TRUE);
INSERT INTO tracking_enterprise (name, carrier) VALUES ('Evergreen', TRUE);
INSERT INTO tracking_enterprise (name, carrier) VALUES ('Scharff', FALSE);

INSERT INTO tracking_container_status (name) VALUES ('Pendiente');
INSERT INTO tracking_container_status (name) VALUES ('Procesado');
INSERT INTO tracking_container_status (name) VALUES ('Procesado con errores');

INSERT INTO tracking_vehicle (name, original_name) VALUES ('Vía marítima (buque)', 'Vessel');
INSERT INTO tracking_vehicle (name, original_name) VALUES ('Vía terrestre (camión)', 'Truck');
INSERT INTO tracking_vehicle (name, original_name) VALUES ('Vía terrestre (tren)', 'Train');
