ALTER TABLE file ADD COLUMN caption TEXT;

UPDATE file
SET caption = confirmation.message
FROM confirmation
WHERE file.id = confirmation.file_id;

ALTER TABLE confirmation DROP COLUMN message;