-- Declare variables
DECLARE @versionStoreSizeMB FLOAT;
DECLARE @totalTempdbSizeMB FLOAT;
DECLARE @versionStoreUsagePct FLOAT;
DECLARE @timeSinceReset DATETIME;

-- Calculate version store size in MB
SELECT @versionStoreSizeMB = SUM(user_object_reserved_page_count + internal_object_reserved_page_count + 
                                  version_store_reserved_page_count + unallocated_extent_page_count) * 8.0 / 1024
FROM sys.dm_db_file_space_usage;

-- Calculate total tempdb size in MB
SELECT @totalTempdbSizeMB = SUM(size) * 8.0 / 1024
FROM tempdb.sys.database_files
WHERE type_desc = 'ROWS';

-- Calculate usage percentage
SET @versionStoreUsagePct = (@versionStoreSizeMB / @totalTempdbSizeMB) * 100;

-- Determine time since last version store reset
SELECT @timeSinceReset = sqlserver_start_time
FROM sys.dm_os_sys_info;

-- Output the results
SELECT 
    @versionStoreSizeMB AS VersionStoreSizeMB,
    @totalTempdbSizeMB AS TotalTempDBSizeMB,
    @versionStoreUsagePct AS VersionStoreUsagePercentage,
    DATEDIFF(MINUTE, @timeSinceReset, GETDATE()) AS MinutesSinceVersionStoreReset;

-- Find top transactions consuming version store space
SELECT 
    TOP 5 
    session_id, 
    transaction_id, 
    elapsed_time_seconds = DATEDIFF(SECOND, transaction_begin_time, GETDATE()), 
    transaction_begin_time
FROM sys.dm_tran_active_snapshot_database_transactions
ORDER BY elapsed_time_seconds DESC;
