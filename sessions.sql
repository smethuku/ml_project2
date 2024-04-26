-- Declare a cursor to loop through active session IDs
DECLARE session_cursor CURSOR FOR
SELECT DISTINCT session_id
FROM sys.dm_tran_active_snapshot_database_transactions
WHERE session_id <> @@SPID;  -- Exclude current session

-- Variable to hold each session ID
DECLARE @SessionID INT;

-- Open the cursor
OPEN session_cursor;

-- Retrieve the first session ID
FETCH NEXT FROM session_cursor INTO @SessionID;

-- Loop through all session IDs
WHILE @@FETCH_STATUS = 0
BEGIN
    -- Execute sp_WhoIsActive for the current session ID
    EXEC sp_WhoIsActive @filter_type = 'session', @filter = @SessionID;

    -- Move to the next session ID
    FETCH NEXT FROM session_cursor INTO @SessionID;
END

-- Cleanup: close and deallocate the cursor
CLOSE session_cursor;
DEALLOCATE session_cursor;
