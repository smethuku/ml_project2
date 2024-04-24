USE TestDB;  -- Ensure you're in the right context for the user database
GO

BEGIN TRANSACTION;

-- Set the isolation level to repeatable read
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Variables to control the loop
DECLARE @i INT = 0;

WHILE @i < 1000  -- Increase the number for a longer test
BEGIN
    -- Update in user database
    UPDATE TestVersionStoreUserDB
    SET DataColumn = 'Updated Data ' + CAST(@i AS VARCHAR(10))
    WHERE ID <= 10;  -- Update a block of rows to increase load

    -- Update in tempdb
    USE tempdb;
    UPDATE TestVersionStoreTempDB
    SET DataColumn = 'Updated TempDB Data ' + CAST(@i AS VARCHAR(10))
    WHERE ID <= 10;  -- Update a block of rows to increase load

    -- Switch back to user DB for next loop iteration
    USE TestDB;

    -- Wait for a bit before the next update
    WAITFOR DELAY '00:00:05';  -- 5 seconds delay to prolong the transaction
    SET @i = @i + 1;
END;

-- Commit or rollback based on your testing requirement
-- COMMIT TRANSACTION;
-- ROLLBACK TRANSACTION;
