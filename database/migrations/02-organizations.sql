\c
"organizations";
CREATE TABLE "organizations"
(
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "license_id" int,
  "owner_id" varchar,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);