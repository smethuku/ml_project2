# Import the Active Directory module
Import-Module ActiveDirectory

# Function to copy members from one AD group to another
function Copy-ADGroupMembers {
    param (
        [string]$SourceGroupName,  # The source AD group name
        [string]$TargetGroupName   # The target AD group name
    )

    # Get members from the source group
    try {
        $sourceGroupMembers = Get-ADGroupMember -Identity $SourceGroupName -ErrorAction Stop
    } catch {
        Write-Error "Failed to retrieve members from source group '$SourceGroupName': $_"
        return
    }

    # Check if the target group exists
    try {
        $targetGroup = Get-ADGroup -Identity $TargetGroupName -ErrorAction Stop
    } catch {
        Write-Error "Target group '$TargetGroupName' not found"
        return
    }

    # Add each member from the source group to the target group
    foreach ($member in $sourceGroupMembers) {
        try {
            Add-ADGroupMember -Identity $TargetGroupName -Members $member -ErrorAction Stop
            Write-Host "Added $($member.SamAccountName) to $TargetGroupName"
        } catch {
            Write-Error "Failed to add $($member.SamAccountName) to $TargetGroupName: $_"
        }
    }
}

# Example usage
# Replace with actual group names
$sourceGroup = "Source_AD_Group_Name"
$targetGroup = "Target_AD_Group_Name"

# Call the function to copy members from source to target group
Copy-ADGroupMembers -SourceGroupName $sourceGroup -TargetGroupName $targetGroup
