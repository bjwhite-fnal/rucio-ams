BEGIN;

-- Running upgrade fe1a65b176c9 -> 1677d4d803c8

ALTER TABLE rses ADD COLUMN availability_read BOOLEAN DEFAULT true;

ALTER TABLE rses ADD COLUMN availability_write BOOLEAN DEFAULT true;

ALTER TABLE rses ADD COLUMN availability_delete BOOLEAN DEFAULT true;

UPDATE rses SET availability_read=false WHERE rses.availability IN (0, 1, 2, 3);

UPDATE rses SET availability_write=false WHERE rses.availability IN (0, 1, 4, 5);

UPDATE rses SET availability_delete=false WHERE rses.availability IN (0, 2, 4, 6);

UPDATE alembic_version SET version_num='1677d4d803c8' WHERE alembic_version.version_num = 'fe1a65b176c9';

-- Running upgrade 1677d4d803c8 -> fa7a7d78b602

ALTER TABLE tokens ALTER COLUMN refresh_token TYPE VARCHAR(3072);

UPDATE alembic_version SET version_num='fa7a7d78b602' WHERE alembic_version.version_num = '1677d4d803c8';

-- Running upgrade fa7a7d78b602 -> d6e2c3b2cf26

ALTER TABLE rse_protocols DROP COLUMN third_party_copy;

UPDATE alembic_version SET version_num='d6e2c3b2cf26' WHERE alembic_version.version_num = 'fa7a7d78b602';

-- Running upgrade d6e2c3b2cf26 -> f41ffe206f37

UPDATE alembic_version SET version_num='f41ffe206f37' WHERE alembic_version.version_num = 'd6e2c3b2cf26';

-- Running upgrade f41ffe206f37 -> 2190e703eb6e

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'city' AS key, city AS value, created_at, updated_at 
FROM rses 
WHERE city IS NOT NULL;

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'region_code' AS key, region_code AS value, created_at, updated_at 
FROM rses 
WHERE region_code IS NOT NULL;

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'country_name' AS key, country_name AS value, created_at, updated_at 
FROM rses 
WHERE country_name IS NOT NULL;

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'continent' AS key, continent AS value, created_at, updated_at 
FROM rses 
WHERE continent IS NOT NULL;

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'time_zone' AS key, time_zone AS value, created_at, updated_at 
FROM rses 
WHERE time_zone IS NOT NULL;

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'ISP' AS key, "ISP" AS value, created_at, updated_at 
FROM rses 
WHERE "ISP" IS NOT NULL;

INSERT INTO rse_attr_map (rse_id, key, value, created_at, updated_at) SELECT id AS rse_id, 'ASN' AS key, "ASN" AS value, created_at, updated_at 
FROM rses 
WHERE "ASN" IS NOT NULL;

UPDATE alembic_version SET version_num='2190e703eb6e' WHERE alembic_version.version_num = 'f41ffe206f37';

COMMIT;

