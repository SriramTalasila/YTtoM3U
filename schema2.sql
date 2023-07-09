DROP TABLE IF EXISTS ext_raw_m3u;
CREATE TABLE ext_raw_m3u (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT  NULL,
    x_tvg_url TEXT  NULL,
    m3u_text TEXT  NULL
);