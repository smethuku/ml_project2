BEGIN TRANSACTION;

-- Variables to control the loop
DECLARE @i INT = 0;
DECLARE @userDB NVARCHAR(128) = N'TestDB';
DECLARE @sql NVARCHAR(MAX);

WHILE @i < 100
BEGIN
    -- Update in user database
    SET @sql = 'UPDATE ' + @userDB + '.dbo.TestVersionStoreUserDB SET DataColumn = ''Updated Data '' + CAST(' + CAST(@i AS NVARCHAR(10)) + ' AS VARCHAR(10)) WHERE ID = ' + CAST((@i % 100 + 1) AS NVARCHAR(10)) + ';';
    EXEC sp_executesql @sql;

    -- Update in tempdb
    UPDATE TestVersionStoreTempDB
    SET DataColumn = 'Updated Data ' + CAST(@i AS VARCHAR(10))
    WHERE ID = @i % 100 + 1;  -- Ensure continuous updates

    -- Wait for a bit before the next update
    WAITFOR DELAY '00:00:01';  -- 1 second delay, adjust as necessary
    SET @i = @i + 1;
END;

-- Optionally, commit or rollback the transaction
-- COMMIT;
-- ROLLBACK;
