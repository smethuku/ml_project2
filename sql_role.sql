USE [<USER DBNAME>]
GO
CREATE ROLE [<Name>_dbdatareader] 
GO
GRANT SELECT ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatareader] 
GO

CREATE ROLE [<Name>_dbdatawriter]
GO
GRANT DELETE ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatawriter]
GO
GRANT INSERT ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatawriter]
GO
GRANT REFERENCES ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatawriter]
GO
GRANT SELECT ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatawriter]
GO
GRANT UPDATE ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatawriter]
GO

CREATE ROLE [<Name>_executer]
GO
GRANT EXECUTE ON SCHEMA::[<SCHEMA NAME>] To [<Name>_executer]
GO

CREATE ROLE [<Name>_ddladmin] 
GO
GRANT ALTER ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT DELETE ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT EXECUTE ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT INSERT ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT REFERENCES ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT SELECT ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT UPDATE ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO
GRANT VIEW DEFINITION ON SCHEMA::[<SCHEMA NAME>] To [<Name>_ddladmin] 
GO

CREATE ROLE [<Name>_viewdef] 
GO
GRANT VIEW DEFINITION ON SCHEMA::[<SCHEMA NAME>] To [<Name>_dbdatareader] 
GO
