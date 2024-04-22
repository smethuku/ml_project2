# Import SQL Server module
Import-Module SqlServer

# SQL Server instance
$serverInstance = "YourSqlServerInstance"

# Query to get physical file paths of tempdb files
$queryFilePaths = @"
SELECT 
    physical_name 
FROM 
    sys.master_files
WHERE 
    database_id = DB_ID('tempdb');
"@

# Execute SQL query to get file paths
$filePaths = Invoke-Sqlcmd -Query $queryFilePaths -ServerInstance $serverInstance

# Get unique mount points from file paths
$mountPoints = $filePaths | Select-Object -ExpandProperty physical_name | ForEach-Object {
    Split-Path -Path $_ -Qualifier
} | Sort-Object -Unique

# Check disk space for each mount point
foreach ($mount in $mountPoints) {
    # Retrieve disk space info using Get-WmiObject
    $disk = Get-WmiObject -Query "SELECT * FROM Win32_LogicalDisk WHERE DeviceID='$mount'"

    if ($disk -eq $null) {
        Write-Host "Mount point $mount is not accessible or does not exist."
        continue
    }

    # Calculate percentage free space
    $percentFree = ($disk.FreeSpace / $disk.Size) * 100

    # Check if mount point has at least 10% free of its total space
    if ($percentFree -lt 10) {
        Write-Host "Not enough disk space on mount point $mount. At least 10% of total disk space is required."
        continue
    }

    Write-Host "Mount point $mount has sufficient space."

    # Proceed with other operations, assuming checks are done for all mount points before proceeding
    # Further operations like file size calculations and resizing can now safely proceed
}

# Further operations to resize tempdb files should be placed here
# Follow the previous example scripts to add resizing logic
