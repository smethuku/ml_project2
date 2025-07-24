function Update-SqlObjectLinkedServerReference {
    param (
        [string]$ServerName,
        [string]$DatabaseName,
        [ValidateSet("StoredProcedure", "View", "Function", "All")]
        [string]$ObjectType = "All",
        [string]$SourceSqlText,
        [string]$ReplaceSqlText
    )

    # Load SMO
    Add-Type -AssemblyName "Microsoft.SqlServer.SMO"

    $server = New-Object Microsoft.SqlServer.Management.Smo.Server $ServerName
    $db = $server.Databases[$DatabaseName]

    $updatedObjects = [PSCustomObject]@{
        StoredProcedures = @()
        Views            = @()
        Functions        = @()
    }

    if ($ObjectType -in @("StoredProcedure", "All")) {
        foreach ($sp in $db.StoredProcedures) {
            if (-not $sp.IsSystemObject -and $sp.TextHeader -and $sp.TextBody -like "*$SourceSqlText*") {
                $newBody = $sp.TextBody -replace [regex]::Escape($SourceSqlText), $ReplaceSqlText
                $alterScript = "$($sp.TextHeader)`n$newBody"

                $server.Databases[$DatabaseName].ExecuteNonQuery($alterScript)
                $updatedObjects.StoredProcedures += "$($sp.Schema).$($sp.Name)"
            }
        }
    }

    if ($ObjectType -in @("View", "All")) {
        foreach ($view in $db.Views) {
            if (-not $view.IsSystemObject -and $view.TextHeader -and $view.TextBody -like "*$SourceSqlText*") {
                $newBody = $view.TextBody -replace [regex]::Escape($SourceSqlText), $ReplaceSqlText
                $alterScript = "$($view.TextHeader)`n$newBody"

                $server.Databases[$DatabaseName].ExecuteNonQuery($alterScript)
                $updatedObjects.Views += "$($view.Schema).$($view.Name)"
            }
        }
    }

    if ($ObjectType -in @("Function", "All")) {
        foreach ($fn in $db.UserDefinedFunctions) {
            if ($fn.IsSystemObject -eq $false -and $fn.TextHeader -and $fn.TextBody -like "*$SourceSqlText*") {
                $newBody = $fn.TextBody -replace [regex]::Escape($SourceSqlText), $ReplaceSqlText
                $alterScript = "$($fn.TextHeader)`n$newBody"

                $server.Databases[$DatabaseName].ExecuteNonQuery($alterScript)
                $updatedObjects.Functions += "$($fn.Schema).$($fn.Name)"
            }
        }
    }

    return $updatedObjects
}
