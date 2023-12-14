BEGIN;

-- Running upgrade 9a45bc4ea66d -> 0f1adb7a599a

CREATE TABLE transfer_hops (
    request_id UUID, 
    next_hop_request_id UUID, 
    initial_request_id UUID, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

ALTER TABLE transfer_hops ADD CONSTRAINT "TRANSFER_HOPS_PK" PRIMARY KEY (request_id, next_hop_request_id, initial_request_id);

ALTER TABLE transfer_hops ADD CONSTRAINT "TRANSFER_HOPS_INIT_REQ_ID_FK" FOREIGN KEY(initial_request_id) REFERENCES requests (id);

ALTER TABLE transfer_hops ADD CONSTRAINT "TRANSFER_HOPS_REQ_ID_FK" FOREIGN KEY(request_id) REFERENCES requests (id);

ALTER TABLE transfer_hops ADD CONSTRAINT "TRANSFER_HOPS_NH_REQ_ID_FK" FOREIGN KEY(next_hop_request_id) REFERENCES requests (id);

ALTER TABLE transfer_hops ADD CONSTRAINT "TRANSFER_HOPS_CREATED_NN" CHECK (created_at is not null);

ALTER TABLE transfer_hops ADD CONSTRAINT "TRANSFER_HOPS_UPDATED_NN" CHECK (updated_at is not null);

CREATE INDEX "TRANSFER_HOPS_INITIAL_REQ_IDX" ON transfer_hops (initial_request_id);

CREATE INDEX "TRANSFER_HOPS_NH_REQ_IDX" ON transfer_hops (next_hop_request_id);

UPDATE alembic_version SET version_num='0f1adb7a599a' WHERE alembic_version.version_num = '9a45bc4ea66d';

-- Running upgrade 0f1adb7a599a -> fe1a65b176c9

UPDATE rse_protocols SET third_party_copy_read=third_party_copy WHERE third_party_copy_read is NULL;

UPDATE rse_protocols SET third_party_copy_write=third_party_copy WHERE third_party_copy_write is NULL;

ALTER TABLE rse_protocols ALTER COLUMN third_party_copy_read SET DEFAULT '0';

ALTER TABLE rse_protocols ALTER COLUMN third_party_copy_write SET DEFAULT '0';

UPDATE alembic_version SET version_num='fe1a65b176c9' WHERE alembic_version.version_num = '0f1adb7a599a';

COMMIT;

