create table if not exists users
(
	id serial not null
		constraint users_pkey
			primary key,
	email text not null
		constraint users_email_key
			unique,
	username text not null
		constraint users_username_key
			unique,
	image_url text,
	header_image_url text,
	bio text,
	location text,
	password text not null
);

alter table users owner to acampos;

create table if not exists follows
(
	user_being_followed_id integer not null
		constraint follows_user_being_followed_id_fkey
			references users
				on delete cascade,
	user_following_id integer not null
		constraint follows_user_following_id_fkey
			references users
				on delete cascade,
	constraint follows_pkey
		primary key (user_being_followed_id, user_following_id)
);

alter table follows owner to acampos;

create table if not exists messages
(
	id serial not null
		constraint messages_pkey
			primary key,
	text varchar(140) not null,
	timestamp timestamp not null,
	user_id integer not null
		constraint messages_user_id_fkey
			references users
				on delete cascade
);

alter table messages owner to acampos;

create table if not exists likes
(
	id serial not null
		constraint likes_pkey
			primary key,
	user_id integer
		constraint likes_user_id_fkey
			references users
				on delete cascade,
	message_id integer
		constraint likes_message_id_key
			unique
		constraint likes_message_id_fkey
			references messages
				on delete cascade
);

alter table likes owner to acampos;

