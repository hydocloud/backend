\c
"devices";
CREATE TABLE "device_groups"
(
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "organization_id" int,
  "owner_id" uuid NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "devices"
(
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL,
  "serial" uuid NOT NULL,
  "device_group_id" int NOT NULL,
  "hmac_key" bytea NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now()),
  UNIQUE("device_id", "device_group_id")
);

ALTER TABLE "devices" ADD FOREIGN KEY ("device_group_id") REFERENCES "device_groups" ("id") ON DELETE CASCADE;