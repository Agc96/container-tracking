-- Estado 1
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (1, 'Empty', 1);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (1, 'Gate out empty', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (1, 'Empty pick-up by merchant haulage', 3);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (1, 'Retiro de vacío', 4);
-- Estado 2
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (2, 'Gate in', 1);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (2, 'Arrival in', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (2, 'Received (FCL)', 3);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (2, 'Llegada de contenedor a puerto', 4);
-- Estado 3
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (3, 'Load', 1);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (3, 'Loaded', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (3, 'Loaded (FCL) on vessel', 3);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (3, 'Contenedor cargado en barco', 4);
-- Estado 4
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (4, 'Vessel departed', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (4, 'Vessel departure', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (4, 'Salida de barco', 4);
-- Estado 5
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (5, 'Vessel arrived', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (5, 'Vessel arrival', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (5, 'Transbordo', 4);
-- Estado 6
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (6, 'Llegada de barco', 4);
-- Estado 7
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (7, 'Discharge', 1);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (7, 'Discharged', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (7, 'Discharged (FCL)', 3);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (7, 'Descarga del barco', 4);
-- Estado 8
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (0, 'Gate out', 1);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (0, 'Departure from', 2);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (0, 'Pick-up by merchant haulage', 3);
INSERT INTO tracking_movement_status (status, name, enterprise_id) VALUES (0, 'Retiro', 4);
