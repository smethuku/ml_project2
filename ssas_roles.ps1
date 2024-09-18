function Create-SSASRoles {
    param (
        [string]$instanceName,
        [string]$databaseName,
        [string]$roleName
    )

    # Load the necessary assemblies for SSAS
    [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.AnalysisServices") | Out-Null

    # Connect to the SSAS server
    $server = New-Object Microsoft.AnalysisServices.Server
    try {
        $server.Connect($instanceName)
    } catch {
        Write-Host "Could not connect to SSAS instance: $instanceName" -ForegroundColor Red
        return
    }

    # Check if the database exists on the server
    $database = $server.Databases.FindByName($databaseName)
    if ($null -eq $database) {
        Write-Host "Database '$databaseName' does not exist on the server '$instanceName'." -ForegroundColor Yellow
        return
    }

    Write-Host "Database '$databaseName' exists. Proceeding to create roles..." -ForegroundColor Green

    # Check if the role already exists
    $existingRole = $database.Roles.FindByName($roleName)
    if ($existingRole) {
        Write-Host "Role '$roleName' already exists. No need to create it." -ForegroundColor Yellow
    } else {
        # Create a new role
        $role = New-Object Microsoft.AnalysisServices.Role
        $role.Name = $roleName
        $role.ID = $roleName
        $role.Description = "Role with Read Definition on database and Read on cubes"
        $database.Roles.Add($role)

        # Assign Read Definition permission to the database
        $dbPermission = New-Object Microsoft.AnalysisServices.DatabasePermission
        $dbPermission.ID = $role.ID
        $dbPermission.ReadDefinition = [Microsoft.AnalysisServices.ReadDefinition]::Allowed
        $role.DatabasePermissions.Add($dbPermission)

        # Assign Read permission to all cubes in the database
        foreach ($cube in $database.Cubes) {
            $cubePermission = New-Object Microsoft.AnalysisServices.CubePermission
            $cubePermission.ID = $role.ID
            $cubePermission.Read = [Microsoft.AnalysisServices.ReadAccess]::Allowed
            $cube.CubePermissions.Add($cubePermission)
        }

        # Update the database with the new role and permissions
        try {
            $database.Update()
            Write-Host "Role '$roleName' created and permissions assigned successfully." -ForegroundColor Green
        } catch {
            Write-Host "Failed to update the database with the new role. Error: $_" -ForegroundColor Red
        }
    }

    # Disconnect from the server
    $server.Disconnect()
}

# Example usage of the function
Create-SSASRoles -instanceName "YourServer\SSASInstance" -databaseName "YourDatabaseName" -roleName "NewRoleName"
