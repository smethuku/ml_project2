# Import necessary modules
Import-Module ActiveDirectory
Import-Module SQLPS # Or Microsoft.AnalysisServices

# Define function to get role members from SSAS
function Get-SSASRoleMembers {
    param (
        [string]$SSASInstance,
        [string]$DatabaseName,
        [string]$RoleName
    )

    # Connect to the SSAS instance
    $connectionString = "Data Source=$SSASInstance"
    $server = New-Object Microsoft.AnalysisServices.Server
    $server.Connect($connectionString)

    # Find the database
    $database = $server.Databases[$DatabaseName]

    if (-not $database) {
        Write-Error "Database $DatabaseName not found on SSAS instance $SSASInstance"
        return
    }

    # Find the role
    $role = $database.Roles[$RoleName]
    
    if (-not $role) {
        Write-Error "Role $RoleName not found in SSAS database $DatabaseName"
        return
    }

    # Get members of the SSAS role
    $roleMembers = $role.Members
    $roleMembersDN = @()

    foreach ($member in $roleMembers) {
        $roleMembersDN += $member.Name
    }

    $server.Disconnect()

    return $roleMembersDN
}

# Define function to add members to AD group
function Add-MembersToADGroup {
    param (
        [string]$ADGroupName,
        [string[]]$MembersDN
    )

    # Check if AD group exists
    $adGroup = Get-ADGroup -Filter { Name -eq $ADGroupName }
    
    if (-not $adGroup) {
        Write-Error "AD Group $ADGroupName not found"
        return
    }

    foreach ($member in $MembersDN) {
        try {
            Add-ADGroupMember -Identity $ADGroupName -Members $member -ErrorAction Stop
            Write-Host "Successfully added $member to AD group $ADGroupName"
        } catch {
            Write-Error "Failed to add $member to AD group $ADGroupName: $_"
        }
    }
}

# Main script logic
param (
    [string]$SSASInstance,
    [string]$DatabaseName,
    [string]$SSASRoleName,
    [string]$ADGroupName
)

# Get role members from SSAS
$roleMembers = Get-SSASRoleMembers -SSASInstance $SSASInstance -DatabaseName $DatabaseName -RoleName $SSASRoleName

if ($roleMembers) {
    # Add role members to AD group
    Add-MembersToADGroup -ADGroupName $ADGroupName -MembersDN $roleMembers
} else {
    Write-Error "No members found in SSAS role or error occurred while fetching members."
}
