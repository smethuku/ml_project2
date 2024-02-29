SET NOCOUNT ON
BEGIN Try
Declare @5minsago varchar(100)
set @5minsago = format(DATEADD(MINUTE, -5, GetDate()),'yyyyMMddHHmmssffff')

DECLARE @tbl_output TABLE([Node] nvarchar(50), TimeGenerated datetime2, Msg nvarchar(max))
DECLARE @sql VARCHAR(500) = 'WMIC NTEVENT WHERE '+'"'+'LogFile='+'''System'''+' AND SourceName= '+'''Microsoft-Windows-FailoverClustering'''+' and EventCode = '+'''1069'''+'"'+' GET TimeGenerated, Message  /Format:csv' 

INSERT INTO @tbl_output([Node],TimeGenerated,Msg)
Exec Master..xp_cmdshell @sql
Select * from @tbl_output
END try
BEGIN CATCH
SELECT 'Failed to execute the query'
END Catch

-- Assume @tbl_output is already declared and @sql is set
-- Execute the command and capture the output in a temporary table or table variable
DECLARE @cmdOutput TABLE (CmdOutput NVARCHAR(MAX));

INSERT INTO @cmdOutput
EXEC master..xp_cmdshell @sql;

-- Process @cmdOutput to extract CSV data
-- This step is highly dependent on the exact format of your CSV and might involve
-- complex string manipulation or a more sophisticated parsing approach

-- An example of processing might look like iterating over each line,
-- checking for valid CSV format, and then inserting into @tbl_output
-- Note: This is a conceptual example and not directly executable as-is
DECLARE @Line NVARCHAR(MAX);

DECLARE cursor_name CURSOR FOR
SELECT CmdOutput FROM @cmdOutput WHERE CmdOutput IS NOT NULL AND CmdOutput != 'No Instance(s) Available.' AND CmdOutput NOT LIKE '%Node,TimeGenerated,Message%';

OPEN cursor_name;
FETCH NEXT FROM cursor_name INTO @Line;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Parse @Line to split by ',' and insert into @tbl_output
    -- This is where CSV parsing logic would be applied
    FETCH NEXT FROM cursor_name INTO @Line;
END;

CLOSE cursor_name;
DEALLOCATE cursor_name;

-- Now, @tbl_output should contain the parsed data
SELECT * FROM @tbl_output;



 
Node,Message,TimeGenerated 
Node1,Cluster resource 'Cluster IP Address 00.00.00.0' of type 'IP Address' in clustered role 'Cluster Group' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240229153752.663279-000 
Node1,Cluster resource 'Cluster IP Address 00.00.00.0' of type 'IP Address' in clustered role 'Cluster Group' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240229013651.761247-000 
Node1,Cluster resource 'Cluster IP Address 00.00.00.0' of type 'IP Address' in clustered role 'Cluster Group' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240228231111.229901-000 
Node1,Cluster resource 'ASTAG-SQL910AT_10.27.41.241' of type 'IP Address' in clustered role 'ASTAG-SQL910AT' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240220140651.034371-000 
Node1,Cluster resource 'ASTAG-SQL910AT_10.27.41.241' of type 'IP Address' in clustered role 'ASTAG-SQL910AT' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240220140645.800692-000 
Node1,Cluster resource 'Cluster IP Address 00.00.00.0' of type 'IP Address' in clustered role 'Cluster Group' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240216014123.033565-000 
Node1,Cluster resource 'ASTAG-SQL910AT_10.27.41.241' of type 'IP Address' in clustered role 'ASTAG-SQL910AT' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240216012855.980842-000 
Node1,Cluster resource 'ASTAG-SQL910AT_10.27.41.241' of type 'IP Address' in clustered role 'ASTAG-SQL910AT' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240216012845.438566-000 
Node1,Cluster resource 'File Share Witness' of type 'File Share Witness' in clustered role 'Cluster Group' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240213022930.346149-000 
Node1,Cluster resource 'File Share Witness' of type 'File Share Witness' in clustered role 'Cluster Group' failed. 
 
Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.,20240213021530.113581-000 
NULL
