-- Step 1: Create a login at the server level

CREATE LOGIN APILogin

WITH PASSWORD = 'MI$T460Instructor';



-- Step 2: Switch to your target database
GO

USE mist460-api-group1;

GO

-- Step 3: Create a database user mapped to the login

CREATE USER APIUser

FOR LOGIN APILogin;



-- Step 4: Grant EXECUTE permission on all stored procedures and UDFs

GRANT EXECUTE TO APIUser;



-- Read access to all tables

GRANT SELECT TO APIUser;