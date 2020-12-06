CREATE TABLE "user_groups" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "organization_id" int,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "user_belong_user_groups" (
  "id" SERIAL PRIMARY KEY,
  "user_id" uuid,
  "user_group_id" int UNIQUE,
  "attributes" varchar,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);

ALTER TABLE "user_groups" ADD FOREIGN KEY ("id") REFERENCES "user_belong_user_groups" ("user_group_id");
