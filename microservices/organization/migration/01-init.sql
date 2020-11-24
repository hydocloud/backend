-- SQL dump generated using DBML (dbml-lang.org)
-- Database: PostgreSQL
-- Generated at: 2020-11-15T19:47:42.616Z

CREATE TABLE "organizations" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "license_id" int,
  "owner_id" varchar,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);
