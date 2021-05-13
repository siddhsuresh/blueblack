/* DEFERRABLE INITIALLY DEFERRED - checking will be deferred to just before each transaction commits */
CREATE TABLE IF NOT EXISTS "library_author"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" varchar(100) NOT NULL,
  "gender" varchar(15) NOT NULL,
  "nationality" varchar(50) NOT NULL,
  "bio" varchar(1000) NOT NULL
);
CREATE TABLE IF NOT EXISTS "library_book"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "title" varchar(200) NOT NULL,
  "summary" text NOT NULL,
  "isbn" varchar(13) NOT NULL UNIQUE,
  "total_book" integer NOT NULL,
  "available_books" integer NOT NULL,
  "author_id" bigint NULL REFERENCES "library_author"("id") DEFERRABLE INITIALLY DEFERRED,
  "language_id" bigint NULL REFERENCES "library_language"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "library_book_author_id_d9a3b67e" ON "library_book"("author_id");
CREATE INDEX "library_book_language_id_db0f140f" ON "library_book"(
  "language_id"
);
CREATE TABLE IF NOT EXISTS "library_book_genre"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "book_id" bigint NOT NULL REFERENCES "library_book"("id") DEFERRABLE INITIALLY DEFERRED,
  "genre_id" bigint NOT NULL REFERENCES "library_genre"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE UNIQUE INDEX "library_book_genre_book_id_genre_id_c685f9b3_uniq" ON "library_book_genre"(
  "book_id",
  "genre_id"
);
CREATE INDEX "library_book_genre_book_id_b86cda70" ON "library_book_genre"(
  "book_id"
);
CREATE INDEX "library_book_genre_genre_id_f667aa0e" ON "library_book_genre"(
  "genre_id"
);
CREATE TABLE IF NOT EXISTS "library_genre"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" varchar(200) NOT NULL
);
CREATE TABLE IF NOT EXISTS "library_bookindividual"(
  "id" char(32) NOT NULL PRIMARY KEY,
  "edition" integer NOT NULL,
  "status" varchar(1) NOT NULL,
  "book_id" bigint NULL REFERENCES "library_book"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "library_bookindividual_book_id_1d386ec7" ON "library_bookindividual"(
  "book_id"
);
CREATE TABLE IF NOT EXISTS "library_language"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" varchar(200) NOT NULL
);
CREATE TABLE IF NOT EXISTS "library_issuebook"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "issue_date" datetime NULL,
  "expected_return_date" datetime NULL,
  "is_returned" bool NOT NULL,
  "student_id" bigint NOT NULL REFERENCES "library_student"("id") DEFERRABLE INITIALLY DEFERRED,
  "borrowed_book_id" char(32) NULL REFERENCES "library_bookindividual"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "library_issuebook_student_id_0a3b2b22" ON "library_issuebook"(
  "student_id"
);
CREATE INDEX "library_issuebook_borrowed_book_id_3b6c852d" ON "library_issuebook"(
  "borrowed_book_id"
);
CREATE TABLE IF NOT EXISTS "library_returnbook"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "actual_return_date" datetime NULL,
  "is_fined" bool NOT NULL,
  "borrowed_book_id" bigint NULL UNIQUE REFERENCES "library_issuebook"("id") DEFERRABLE INITIALLY DEFERRED,
  "student_id" bigint NOT NULL REFERENCES "library_student"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "library_returnbook_student_id_5800ade0" ON "library_returnbook"(
  "student_id"
);
CREATE TABLE IF NOT EXISTS "library_student"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" varchar(20) NOT NULL,
  "branch" varchar(3) NOT NULL,
  "department" varchar(1) NOT NULL,
  "batch" varchar(1) NOT NULL,
  "semester" varchar(1) NOT NULL,
  "total_books_due" integer NOT NULL,
  "fine" integer NOT NULL,
  "email" varchar(254) NOT NULL,
  "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED,
  "roll_no" varchar(10) NOT NULL
);
CREATE TABLE IF NOT EXISTS "auth_user"(
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "password" varchar(128) NOT NULL,
  "last_login" datetime NULL,
  "is_superuser" bool NOT NULL,
  "username" varchar(150) NOT NULL UNIQUE,
  "last_name" varchar(150) NOT NULL,
  "email" varchar(254) NOT NULL,
  "is_staff" bool NOT NULL,
  "is_active" bool NOT NULL,
  "date_joined" datetime NOT NULL,
  "first_name" varchar(150) NOT NULL
);