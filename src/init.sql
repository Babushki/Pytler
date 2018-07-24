DROP DATABASE IF EXISTS pytler;

CREATE DATABASE pytler;
\connect pytler

CREATE TABLE users (
    id serial PRIMARY KEY,
    login varchar(32) UNIQUE NOT NULL,
    password varchar(64) NOT NULL,
    email varchar(254) UNIQUE NOT NULL,
    created_at bigint NOT NULL,
    activated boolean DEFAULT FALSE NOT NULL,
    profile_image bytea,
    description varchar(100)
);

CREATE TABLE call_history (
    id serial PRIMARY KEY,
    caller_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    datetime bigint NOT NULL,
    duration bigint
);

CREATE TABLE sessions (
    id serial PRIMARY KEY,
    user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at bigint NOT NULL,
    expiration_date bigint NOT NULL
);

CREATE TABLE key_types (
    id serial PRIMARY KEY,
    name varchar(255) UNIQUE NOT NULL
);

CREATE TABLE keys (
    id serial PRIMARY KEY,
    key_type_id int NOT NULL REFERENCES key_types(id) ON DELETE CASCADE,
    user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    value varchar(255) NOT NULL,
    expiration_date bigint NOT NULL
);

CREATE TABLE invitation_statuses (
    id serial PRIMARY KEY,
    name varchar(20) UNIQUE NOT NULL
);

CREATE TABLE invitations (
    id serial PRIMARY KEY,
    inviting_user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invited_user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitation_status_id int NOT NULL REFERENCES invitation_statuses(id) ON DELETE CASCADE,
    created_at bigint NOT NULL,
    last_modified bigint NOT NULL
);

CREATE TABLE contacts (
    id serial PRIMARY KEY,
    user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitation_id int NOT NULL REFERENCES invitations(id) ON DELETE CASCADE,
    ringtone bytea
);

CREATE TABLE call_sessions (
    id serial PRIMARY KEY,
    user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversator_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at bigint NOT NULL,
    expiration_date bigint NOT NULL
);

CREATE TABLE pending_calls (
    id serial PRIMARY KEY,
    calling_user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    called_user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_host varchar(20) NOT NULL,
    address_port int NOT NULL,
    encrypted boolean NOT NULL DEFAULT FALSE,
    public_key varchar(2500)
);

INSERT INTO invitation_statuses (name) VALUES ('pending'), ('accepted'), ('rejected_unseen'), ('rejected');
INSERT INTO key_types (name) VALUES ('activation');
