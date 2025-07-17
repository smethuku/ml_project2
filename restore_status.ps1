param (
    [string]$ServerName,
    [string]$DatabaseName
)

Import-Module SqlServer -ErrorAction Stop

# Connect using SMO
try {
    $smoServer = New-Object Microsoft.SqlServer.Management.Smo.Server $ServerName
} catch {
    Write-Error "Failed to connect to SQL Server via SMO. $_"
    return
}

# Step 1: Get restore start time and sql_text
$restoreQuery = @"
SELECT 
    r.session_id,
    r.command,
    r.percent_complete,
    r.start_time,
    st.text AS sql_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
WHERE r.command = 'RESTORE DATABASE'
"@

try {
    $restoreRequests = Invoke-Sqlcmd -ServerInstance $ServerName -Query $restoreQuery -ErrorAction Stop
} catch {
    Write-Error "Failed to retrieve restore information. $_"
    return
}

# Step 2: Filter by database name in SQL text
$matchedRestore = $restoreRequests | Where-Object { $_.sql_text -match "(?i)\b$DatabaseName\b" }

if (-not $matchedRestore) {
    Write-Output "No active RESTORE DATABASE command found for $DatabaseName."
    return
}

$sqlText = $matchedRestore.sql_text
$restoreStartTime = Get-Date $matchedRestore.start_time

# Step 3: Count number of transaction logs to restore
$logRestoreCount = ([regex]::Matches($sqlText, "(?i)RESTORE LOG")).Count

Write-Output "Restore started at: $restoreStartTime"
Write-Output "Transaction Log Backups to be restored: $logRestoreCount"

# Step 4: Monitor progress in loop
$logRestoresCompleted = 0
$lastRestoreTime = $null

while ($true) {
    $db = $smoServer.Databases[$DatabaseName]
    $status = if ($db) { $db.Status.ToString() } else { "Not Yet Created" }

    # Check if DB is online
    if ($status -eq "Normal") {
        Write-Output "Database [$DatabaseName] is now ONLINE."
        if ($lastRestoreTime) {
            Write-Output "Last transaction log restore completed at: $lastRestoreTime"
        }
        break
    }

    # Query msdb.dbo.restorehistory for completed restores
    $historyQuery = @"
SELECT 
    restore_date,
    restore_type,
    backup_set_id,
    [user_name]
FROM msdb.dbo.restorehistory
WHERE destination_database_name = '$DatabaseName'
AND restore_date >= '$($restoreStartTime.ToString("yyyy-MM-dd HH:mm:ss"))'
ORDER BY restore_date ASC
"@

    $restoreHistory = Invoke-Sqlcmd -ServerInstance $ServerName -Query $historyQuery

    # Determine current restore phase
    $completedCount = $restoreHistory.Count
    $lastRestore = $restoreHistory | Select-Object -Last 1
    $lastRestoreTime = $lastRestore.restore_date

    $currentRestoreQuery = @"
SELECT 
    r.command,
    r.percent_complete,
    st.text AS sql_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
WHERE r.command LIKE 'RESTORE%'
"@

    $currentRestore = Invoke-Sqlcmd -ServerInstance $ServerName -Query $currentRestoreQuery |
                      Where-Object { $_.sql_text -match "(?i)\b$DatabaseName\b" }

    if ($currentRestore) {
        $command = $currentRestore.command
        $percent = [math]::Round($currentRestore.percent_complete, 2)

        if ($command -eq "RESTORE DATABASE") {
            if ($completedCount -eq 0) {
                Write-Output "Restoring FULL backup now... $percent% complete"
            } elseif ($completedCount -eq 1 -and $restoreHistory[0].restore_type -eq 'D') {
                Write-Output "Restoring DIFFERENTIAL backup now... $percent% complete"
            } else {
                Write-Output "Restoring additional DATABASE restore (possible DIFF)... $percent% complete"
            }
        }
        elseif ($command -eq "RESTORE LOG") {
            $logNumber = $restoreHistory | Where-Object { $_.restore_type -eq 'L' } | Measure-Object | Select-Object -ExpandProperty Count
            $logNumber += 1
            Write-Output "Restoring $logNumber of $logRestoreCount Transaction Log backups... $percent% complete"
        } else {
            Write-Output "Restore in progress: $command - $percent% complete"
        }
    } else {
        Write-Output "Waiting for next restore to start..."
    }

    Start-Sleep -Seconds 5
}
