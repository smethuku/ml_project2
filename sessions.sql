-- Create a temporary table to store results
IF OBJECT_ID('tempdb..#WhoIsActiveResults') IS NOT NULL
    DROP TABLE #WhoIsActiveResults;

CREATE TABLE #WhoIsActiveResults (
    [dd hh:mm:ss.mss] VARCHAR(20),
    [session_id] INT,
    [sql_text] NVARCHAR(MAX),
    [login_name] NVARCHAR(128),
    [wait_info] NVARCHAR(4000),
    [CPU] VARCHAR(30),
    [tempdb_allocations] VARCHAR(30),
    [tempdb_current] VARCHAR(30),
    [blocking_session_id] INT,
    [reads] VARCHAR(30),
    [writes] VARCHAR(30),
    [physical_reads] VARCHAR(30),
    [query_plan] XML,
    [used_memory] INT,
    [status] NVARCHAR(60),
    [tran_log_writes] VARCHAR(30),
    [host_name] NVARCHAR(128),
    [database_name] NVARCHAR(128),
    [program_name] NVARCHAR(128)
);

-- Note: Adjust the column list based on the information you need and the output of sp_WhoIsActive
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
    -- Execute sp_WhoIsActive for the current session ID and insert the results into the temp table
    INSERT INTO #WhoIsActiveResults
    EXEC sp_WhoIsActive @filter_type = 'session', @filter = @SessionID, @get_plans = 1, @get_additional_info = 1;

    -- Move to the next session ID
    FETCH NEXT FROM session_cursor INTO @SessionID;
END

-- Cleanup: close and deallocate the cursor
CLOSE session_cursor;
DEALLOCATE session_cursor;

-- View results
SELECT *
FROM #WhoIsActiveResults
