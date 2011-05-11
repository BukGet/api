
CREATE TABLE repositories (
  id          MEDIUMINT           NOT NULL AUTO_INCREMENT PRIMARY KEY,
  author      CHAR(32)            NOT NULL,
  email       CHAR(128)           NOT NULL,
  url         TEXT                NOT NULL,
  plugin      CHAR(32)            NOT NULL UNIQUE,
  created     DATETIME            NOT NULL,
  activated   BOOLEAN             NOT NULL DEFAULT 0,
  hash        CHAR(32)            NOT NULL
);