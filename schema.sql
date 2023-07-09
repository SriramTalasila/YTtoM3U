DROP TABLE IF EXISTS channels;

CREATE TABLE channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    src_url TEXT NOT NULL,
    manifest_url TEXT NULL,
    expiry TEXT NOT NULL,
    group_type TEXT NOT NULL,
    is_youtube BOOLEAN NOT NULL DEFAULT false,
    tvg_img TEXT NOT NULL
);

