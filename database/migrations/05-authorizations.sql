\c
"authorizations";
CREATE TABLE "authorizations" (
  "id" SERIAL PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "device_id" int NOT NULL,
  "start_time" timestamp NOT NULL DEFAULT (now()),
  "end_time" timestamp,
  "access_limit" int,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "updated_at" timestamp NOT NULL DEFAULT (now())
);