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

