BEGIN;

-- Running upgrade 739064d31565 -> 9a45bc4ea66d

CREATE TABLE virtual_placements (
    scope VARCHAR(25), 
    name VARCHAR(250), 
    placements JSONB, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

ALTER TABLE virtual_placements ADD CONSTRAINT "VIRTUAL_PLACEMENTS_PK" PRIMARY KEY (scope, name);

ALTER TABLE virtual_placements ADD CONSTRAINT "VP_FK" FOREIGN KEY(scope, name) REFERENCES dids (scope, name);

UPDATE alembic_version SET version_num='9a45bc4ea66d' WHERE alembic_version.version_num = '739064d31565';

COMMIT;

