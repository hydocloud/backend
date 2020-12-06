CREATE TABLE "user_groups" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "organization_id" int
);

CREATE TABLE "user_belong_user_groups" (
  "id" SERIAL PRIMARY KEY,
  "user_id" uuid,
  "user_group_id" int,
  "attributes" varchar
);