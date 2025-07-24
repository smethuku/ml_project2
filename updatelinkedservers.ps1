function Fix-LinkedServerReference {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)][string]$ServerName,
        [Parameter(Mandatory=$true)][string]$DatabaseName,
        [Parameter(Mandatory=$true)]
        [ValidateSet('StoredProcedure', 'Function', 'View', 'All')]
        [string]$ObjectType,
        [Parameter(Mandatory=$true)][string]$SourceSqlText,
        [Parameter(Mandatory=$true)][string]$ReplaceSqlText
    )

    try {
        Import-Module SqlServer -ErrorAction Stop
    } catch {
        Write-Error "SqlServer module is required. Run 'Install-Module SqlServer' first."
        return
    }

    $server = New-Object Microsoft.SqlServer.Management.Smo.Server $ServerName
    $db = $server.Databases[$DatabaseName]
    if (-not $db) {
        Write-Error "Database '$DatabaseName' not found on server '$ServerName'"
        return
    }

    # Create list of object types to process
    $typesToProcess = @()
    switch ($ObjectType) {
        'StoredProcedure' { $typesToProcess += 'StoredProcedure' }
        'Function'        { $typesToProcess += 'Function' }
        'View'            { $typesToProcess += 'View' }
        'All'             { $typesToProcess += 'StoredProcedure','Function','View' }
    }

    foreach ($type in $typesToProcess) {
        Write-Host "`nProcessing object type: $type" -ForegroundColor Cyan

        switch ($type) {
            'StoredProcedure' {
                $objects = $db.StoredProcedures | Where-Object { -not $_.IsSystemObject }
            }
            'Function' {
                $objects = $db.UserDefinedFunctions | Where-Object { -not $_.IsSystemObject }
            }
            'View' {
                $objects = $db.Views | Where-Object { -not $_.IsSystemObject }
            }
        }

        foreach ($obj in $objects) {
            $originalText = $obj.TextHeader + "`n" + $obj.TextBody
            if ($originalText -like "*$SourceSqlText*") {
                $newText = $originalText -replace [regex]::Escape($SourceSqlText), $ReplaceSqlText

                Write-Host ">> Found match in [$($obj.Schema)].[$($obj.Name)] - Updating..." -ForegroundColor Yellow

                try {
                    $dropStatement = "DROP $type [$($obj.Schema)].[$($obj.Name)]"
                    $db.ExecuteNonQuery($dropStatement)
                    $db.ExecuteNonQuery($newText)
                    Write-Host ">> Updated [$($obj.Schema)].[$($obj.Name)] successfully." -ForegroundColor Green
                } catch {
                    Write-Error "!! Failed to update [$($obj.Schema)].[$($obj.Name)]: $_"
                }
            } else {
                Write-Host ">> Skipped [$($obj.Schema)].[$($obj.Name)] - No match." -ForegroundColor DarkGray
            }
        }
    }
}
