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



 

Message=Cluster resource 'Cluster IP Address 00.00.00.0' of type 'IP Address' in clustered role 'Cluster Group' failed.



Based on the failure policies for the resource and role, the cluster service may try to bring the resource online on this node or move the group to another node of the cluster and then restart it.  Check the resource and group state using Failover Cluster
 Manager or the Get-ClusterResource Windows PowerShell cmdlet.

TimeGenerated=20240229153752.663279-000


DECLARE @currentText NVARCHAR(MAX);
DECLARE @TimeGeneratedString NVARCHAR(50);
DECLARE @TimeGenerated DATETIME2;

-- Cursor declaration
DECLARE text_cursor CURSOR FOR 
SELECT TextInput FROM InputTexts;

-- Open the cursor
OPEN text_cursor;

-- Fetch from the cursor
FETCH NEXT FROM text_cursor INTO @currentText;

-- Loop through the cursor
WHILE @@FETCH_STATUS = 0
BEGIN
    -- Extract TimeGenerated
    DECLARE @StartIndex INT = CHARINDEX('TimeGenerated=', @currentText) + 14;
    SET @TimeGeneratedString = SUBSTRING(@currentText, @StartIndex, 20); -- Assuming fixed length for TimeGenerated

    -- Convert TimeGeneratedString to DATETIME2
    -- Assuming the format is YYYYMMDDHHMMSS.ffffff
    SET @TimeGenerated = CAST(SUBSTRING(@TimeGeneratedString, 1, 4) + '-' +
                              SUBSTRING(@TimeGeneratedString, 5, 2) + '-' +
                              SUBSTRING(@TimeGeneratedString, 7, 2) + 'T' +
                              SUBSTRING(@TimeGeneratedString, 9, 2) + ':' +
                              SUBSTRING(@TimeGeneratedString, 11, 2) + ':' +
                              SUBSTRING(@TimeGeneratedString, 13, 2) + '.' +
                              SUBSTRING(@TimeGeneratedString, 16, 6) AS DATETIME2);

    -- Insert TimeGenerated into the temp table
    INSERT INTO #TimeGeneratedValues (TimeGenerated)
    VALUES (@TimeGenerated);

    -- Fetch next from the cursor
    FETCH NEXT FROM text_cursor INTO @currentText;
END

-- Close and deallocate the cursor
CLOSE text_cursor;
DEALLOCATE text_cursor;

-- Verify the contents of the temp table
SELECT * FROM #TimeGeneratedValues;


# Define the timeframe to check for recent events (e.g., last 5 minutes)
$timeframe = (Get-Date).AddMinutes(-5)

# Event ID to monitor
$eventID = 1069

# Query the event log
$events = Get-WinEvent -FilterHashtable @{
    LogName = 'System'; 
    ID = $eventID; 
    StartTime = $timeframe
} -ErrorAction SilentlyContinue

if ($events) {
    # Event details to include in the alert
    $eventDetails = $events | ForEach-Object {
        "Time: $($_.TimeCreated); ID: $($_.Id); Message: $($_.Message)"
    } -join "`n"

    # Send an email alert (example using Send-MailMessage)
    $mailParams = @{
        SmtpServer = 'smtp.example.com' # SMTP server
        From = 'alerts@example.com' # Sender address
        To = 'admin@example.com' # Recipient address
        Subject = "Failover Cluster Alert: Event $eventID Detected"
        Body = "The following failover cluster events were detected:`n`n$eventDetails"
    }
    Send-MailMessage @mailParams
} else {
    Write-Host "No recent failover cluster events detected."
}

