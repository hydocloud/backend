\c
"users";
CREATE TABLE "user_groups"
(
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "organization_id" int,
  "owner_id" uuid NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "user_belong_user_groups"
(
  "id" SERIAL PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "user_group_id" int NOT NULL,
  "attributes" varchar,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now()),
  UNIQUE("user_id", "user_group_id")
);

ALTER TABLE "user_belong_user_groups" ADD FOREIGN KEY ("user_group_id") REFERENCES "user_groups" ("id") ON DELETE CASCADE;