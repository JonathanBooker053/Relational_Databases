-- Creating MySQL users for admin and client roles
CREATE USER 'jeopardy_admin'@'localhost' IDENTIFIED BY '10987';
CREATE USER 'jeopardy_client'@'localhost' IDENTIFIED BY '1234';

-- Granting permissions
-- Admin user gets full access to the jeopardydb database
GRANT ALL PRIVILEGES ON jeopardydb.* TO 'jeopardy_admin'@'localhost';

-- Client user gets select access to the jeopardydb database
GRANT SELECT ON jeopardydb.* TO 'jeopardy_client'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;
