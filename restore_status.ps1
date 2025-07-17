function Monitor-RestoreProgress {
    param (
        [string]$ServerName,
        [string]$DatabaseName
    )

    Write-Host "`n--- Starting Restore Monitor ---`n"

    # Step 1: Get the restore start time and sql_text for RESTORE DATABASE
    $restoreQuery = @"
SELECT 
    r.start_time,
    st.text AS sql_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) AS st
WHERE r.command = 'RESTORE DATABASE'
"@

    $restoreInfo = Invoke-Sqlcmd -ServerInstance $ServerName -Query $restoreQuery

    if (!$restoreInfo) {
        Write-Host "No RESTORE DATABASE operation found currently running."
        return
    }

    # Step 2: Filter by database name
    $matchingRow = $restoreInfo | Where-Object { $_.sql_text -match "(?i)$DatabaseName" }

    if (!$matchingRow) {
        Write-Host "No restore found for database [$DatabaseName]."
        return
    }

    $restoreStartTime = $matchingRow.start_time
    $sqlText = $matchingRow.sql_text

    # Step 3: Count RESTORE LOG statements
    $logCount = ([regex]::Matches($sqlText, "(?i)RESTORE\s+LOG")).Count
    Write-Host "Restore started at: $restoreStartTime"
    Write-Host "Total Transaction Logs to restore: $logCount"

    # Loop until database is online
    $server = New-Object Microsoft.SqlServer.Management.Smo.Server $ServerName
    $lastTlogTime = $null

    while ($true) {
        $db = $server.Databases[$DatabaseName]
        
        if ($db -and $db.Status -eq "Normal") {
            Write-Host "`nDatabase [$DatabaseName] is now ONLINE."
            break
        }

        # Step 4: Check msdb.dbo.restorehistory entries after restoreStartTime
        $historyQuery = @"
SELECT restore_date, restore_type
FROM msdb.dbo.restorehistory
WHERE destination_database_name = '$DatabaseName'
AND restore_date >= '$restoreStartTime'
ORDER BY restore_date ASC
"@

        $history = Invoke-Sqlcmd -ServerInstance $ServerName -Query $historyQuery

        $logRestores = $history | Where-Object { $_.restore_type -eq 'L' }
        $numRestoredLogs = $logRestores.Count
        $lastTlogTime = if ($numRestoredLogs -gt 0) { $logRestores[-1].restore_date } else { $null }

        # Step 5: Check for active restore command
        $progressQuery = @"
SELECT r.command, r.percent_complete, r.start_time,
       st.text AS sql_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
WHERE r.command LIKE 'RESTORE%'
"@

        $progressInfo = Invoke-Sqlcmd -ServerInstance $ServerName -Query $progressQuery
        $currentRow = $progressInfo | Where-Object { $_.sql_text -match "(?i)$DatabaseName" }

        if ($currentRow) {
            $percent = [math]::Round($currentRow.percent_complete, 2)
            $cmd = $currentRow.command
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

            if ($cmd -eq "RESTORE DATABASE") {
                if ($currentRow.sql_text -match "(?i)DIFFERENTIAL") {
                    Write-Host "[$timestamp] Restoring Differential Backup - $percent% Completed"
                } else {
                    Write-Host "[$timestamp] Restoring Full Backup - $percent% Completed"
                }
            } elseif ($cmd -eq "RESTORE LOG") {
                $logIndex = $numRestoredLogs + 1
                Write-Host "[$timestamp] Restoring $logIndex of $logCount Transaction Log - $percent% Completed"
            } else {
                Write-Host "[$timestamp] Command: $cmd - $percent% Completed"
            }
        } else {
            Write-Host "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") Waiting for next restore command..."
        }

        Start-Sleep -Seconds 5
    }

    if ($lastTlogTime) {
        Write-Host "Last TLOG Restore completed at: $lastTlogTime"
    } else {
        Write-Host "No Transaction Log restore found in history."
    }

    Write-Host "`n--- Restore Monitor Complete ---`n"
}
