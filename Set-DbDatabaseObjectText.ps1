function Set-DbDatabaseObjectText {
    <#
   .SYNOPSIS
       Find and Update the database object definition
   .DESCRIPTION
       Finds the provided search string and updates the object definition with teh provided replace string
   .NOTES
       Author: Suresh Methuku (suresh.methuku@dimensional.com)
       Create Date: 2025-07-22 
   .PARAMETER dbinstance_name
       The name of the SQL Server instance
   .PARAMETER db_name
       The name of the database
   .PARAMETER object_type
       The type of object type
   .PARAMETER search_text
       The text to search for in various objects
   .PARAMETER replace_to_text
       The text used to replace in various objects
   .EXAMPLE
       Set-DfaDbDatabaseObjectText -dbinstance_name astof-sql910nat -db_name test -object_type ALL -search_text "-prd" -replace_to_text "-dev"    
   .EXAMPLE
       Set-DfaDbDatabaseObjectText -dbinstance_name astof-sql910nat -db_name test -object_type StoredProcedure -search_text "-prd" -replace_to_text "-dev"
   .EXAMPLE
       Set-DfaDbDatabaseObjectText -dbinstance_name astof-sql910nat -db_name test -object_type Function -search_text "-prd" -replace_to_text "-dev"
   .EXAMPLE
       Set-DfaDbDatabaseObjectText -dbinstance_name astof-sql910nat -db_name test -object_type View -search_text "-prd" -replace_to_text "-dev"
   #>
   [CmdletBinding()]
   param (
       [Parameter(Mandatory=$true)][string]$dbinstance_name,
       [Parameter(Mandatory=$true)][string]$db_name,
       [Parameter(Mandatory=$true)][ValidateSet('StoredProcedure', 'Function', 'View', 'All')][string]$object_type,
       [Parameter(Mandatory=$true)][string]$search_text,
       [Parameter(Mandatory=$true)][string]$replace_to_text
   )

  
   $server = Connect-DbaInstance -SqlInstance $dbinstance_name 
   $db = $server.Databases[$db_name]

   $storedProceduresUpdated = @()
   $viewsUpdated            = @()
   $functionsUpdated        = @()
   
   $storedProceduresUpdateFailed = @()
   $viewsUpdateFailed            = @()
   $functionsUpdateFailed        = @()

   $scriptFolder = "D:\Test\";	

   if ($object_type -in @("StoredProcedure", "All")) {
       
       foreach($proc in $db.StoredProcedures | Where-Object { -not $_.IsSystemObject})
       {
           if($proc.TextBody -match $search_text)
           {
                $proc.Script() | Out-File ($scriptFolder + ("Backup_" + [string]$prc.name + ".sql"));   
                Write-Verbose "Processing proc: $($proc.Schema).$($proc.Name)"
                $proc.TextBody = [regex]::replace($proc.TextBody, $search_text , $replace_to_text, "IgnoreCase")	
               Try{
                   $proc.Script() | Out-File ($scriptFolder + ("_" + [string]$prc.name + ".sql"));   
                   $proc.Alter();
                   $storedProceduresUpdated += "$($proc.Schema).$($proc.Name)"
                   }
               catch {
                   $storedProceduresUpdateFailed += "$($proc.Schema).$($proc.Name)"					
                   Write-Error "Updated Failed: $($_.Exception.Message)" -ErrorAction Continue
               }
           }
       }
   }

   if ($object_type -in @("View", "All")) {
       foreach($view in $db.Views | Where-Object { -not $_.IsSystemObject})
       {
           if($view.TextBody -match $search_text)
           {
                
               Write-Verbose "Processing view: $($view.Schema).$($view.Name)"
               $view.Script() | Out-File ($scriptFolder + ("Backup_" + [string]$view.name + ".sql"));
               $view.TextBody = [regex]::replace($view.TextBody, $search_text , $replace_to_text, "IgnoreCase")
               
               Try{
                    $view.Script() | Out-File ($scriptFolder + ("New_" + [string]$view.name + ".sql"));
                    $view.Alter();
                    $viewsUpdated += "$($view.Schema).$($view.Name)"
               }
               catch {
                   $viewsUpdateFailed += "$($view.Schema).$($view.Name)"
                   Write-Error "Updated Failed: $($_.Exception.Message)" -ErrorAction Continue
                   }
               }
           }
   }

   if ($object_type -in @("Function", "All")) {
       foreach($udf in $db.UserDefinedFunctions | Where-Object { -not $_.IsSystemObject})
       {
           if($udf.TextBody -match $search_text)
           {
               Write-Verbose "Processing UDF: $($udf.Schema).$($udf.Name)"
               $udf.Script() | Out-File ($scriptFolder + ("Backup_" + [string]$udf.name + ".sql"));
               $udf.TextBody = [regex]::replace($udf.TextBody, $search_text , $replace_to_text, "IgnoreCase")
               
               Try{
                $udf.Script() | Out-File ($scriptFolder + ("New_" + [string]$udf.name + ".sql"));
                $udf.Alter();
                $functionsUpdated += "$($udf.Schema).$($udf.Name)"
                }
                catch {
                $functionsUpdateFailed += "$($udf.Schema).$($udf.Name)"
                Write-Error "Updated Failed: $($_.Exception.Message)" -ErrorAction Continue
                
                }	
               }
           }
   }

   $result = [PSCustomObject]@{
       StoreProceduresUpdated = if($storedProceduresUpdated.Count -gt 0) {$storedProceduresUpdated} else {@(0)}
       ViewsUpdated           = if($viewsUpdated.Count -gt 0) {$viewsUpdated} else {@(0)}
       FunctionsUpdated       = if($functionsUpdated.Count -gt 0) {$functionsUpdated} else { @(0)}
       StoreProceduresUpdatesFailed = if($storedProceduresUpdateFailed.Count -gt 0) {$storedProceduresUpdateFailed} else {@(0)}
       ViewsUpdatesFailed           = if($viewsUpdateFailed.Count -gt 0) {$viewsUpdateFailed} else {@(0)}
       FunctionsUpdatesFailed      = if($functionsUpdateFailed.Count -gt 0) {$functionsUpdateFailed} else { @(0)}
   }

   Write-Output $result | Format-List

}
