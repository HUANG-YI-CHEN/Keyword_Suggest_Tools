/*
insert Entity Suggest
*/
if not exists( select * from Entity where CName=N'Suggest' and EName=N'Suggest')
	insert into Entity(CName, EName) values(N'Suggest',N'Suggest')
go
/*
update CDes nvarchar(4000) -> nvarchar(max)
*/
alter table object alter column CDes nvarchar(max)
go

if exists( select * from sys.objects where object_id=object_id(N'dbo.fn_getBitValue') and type in ('FT', 'FN', 'FS', 'TF', 'IF') )
	drop function dbo.fn_getBitValue
go
/*
Example:
	declare @Value varbinary(64) = 0x0003
	declare @Position int = 9
	select dbo.fn_getBitValue( @Value, @Position )
Description :
	dbo.fn_getBitValue，確認 BinaryData 在 Position 是否為 1 或 0
*/
create function dbo.fn_getBitValue( @Value varbinary(64), @Position int )
	returns bit
begin
	select @value = iif( isnumeric(@Value) = 1, cast( @value as varbinary(max) ), @value )
	declare @Representation varchar(max) = convert( varchar(max), @Value, 2 )
	select @Representation = replace( @Representation, HexDigit, BinaryDigits )
	from (
		  values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111')
	) as f(HexDigit,BinaryDigits)

	return iif( substring( reverse( @Representation ), @Position, 1 ) = '1', 1, 0)
	--case substring( reverse( @Representation ), @Position, 1 ) when '1' then 1 else 0 end
end
go

if exists( select * from sys.objects where object_id=object_id(N'dbo.fn_updateBitValue') and type in ('FT', 'FN', 'FS', 'TF', 'IF') )
	drop function dbo.fn_updateBitValue
go
/*
Example:
	declare @Value varbinary(64) = 0x0003
	declare @Position int = 9
	declare @BitValue bit = 1
	select dbo.fn_updateBitValue( @Value, @Position, @BitValue )
Description :
	dbo.fn_updateBitValue，取得 BinaryData 修改後的值
*/
create function dbo.fn_updateBitValue( @Value varbinary(64), @Position int, @BitValue bit )
	returns varbinary(max)
begin
	select @value = iif( isnumeric(@Value) = 1, cast( @value as varbinary(max) ), @value )
	declare @Representation varchar(max) = convert( varchar(max), @Value, 2 )

	select @Representation = replace( @Representation, HexDigit, BinaryDigits )
	from (
		  values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111')
	) as f(HexDigit,BinaryDigits)

	select @Representation=iif( len(@Representation)< @Position,
				stuff( reverse( replicate( '0', ((@Position/8)+1)*8-len(@Representation))+@Representation ), @Position, 1 , iif( @BitValue = 1, '1', '0' ) ) ,
				stuff( reverse( @Representation ), @Position, 1 , iif( @BitValue = 1, '1', '0' ) ))
	select @Representation=reverse(@Representation)

	;with ConvertHex as
	(
		select replace( left( @Representation, 4 ), BinaryDigits, HexDigit ) as newHex, left( @Representation, 4 ) as LeftBinary, right( @Representation, len(@Representation)-4 ) as RightBinary
		from ( values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111') ) as f(HexDigit,BinaryDigits)
		where @Representation is not null and len( @Representation)-4 > 0 and BinaryDigits = left( @Representation, 4 )
		union all
		select newHex+replace( left( RightBinary, 4 ), BinaryDigits, HexDigit ), left( RightBinary, 4 ) as LeftBinary,  right( RightBinary, len(RightBinary)-4 )
		from ConvertHex, ( values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111') ) as f(HexDigit,BinaryDigits)
		where LeftBinary is not null and len( RightBinary)-4 > 0 and BinaryDigits = left(  RightBinary, 4 )
		union all
		select newHex+replace( left( RightBinary, 4 ), BinaryDigits, HexDigit ), left( RightBinary, 4 ) as LeftBinary,  right( RightBinary, len(RightBinary)-4 )
		from ConvertHex, ( values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111') ) as f(HexDigit,BinaryDigits)
		where LeftBinary is not null and len( RightBinary)-4 = 0 and BinaryDigits = left(  RightBinary, 4 )
	 )
	 select top 1 @Representation='0x'+newHex from ConvertHex where RightBinary = ''

	return convert( varbinary(max), @Representation, 1)
end
go

if object_id('dbo.fn_getObjectData') is not null
	drop function dbo.fn_getObjectData
go
/*
Example:
	declare @type int = 1
	declare @divisor int = 5
	declare @remainder int = 1
	select * from dbo.fn_getObjectData( @Value, @Position, @BitValue )
Description :
	dbo.fn_getObjectData，取得 Object top 1 Data
*/
create function dbo.fn_getObjectData(
	@eid int,
	@divisor int,
	@remainder int
)
returns table as return(
	-- Databyte (Process bit: N/A | Sentence TP | Text Processor | DOM Parser | Crawler | N/A | N/A | N/A)
    select top 1 o.OID, o.CName, o.CDes, o.Databyte
    from Object o
    where Type = @eid and o.OID % @divisor = @remainder and dbo.fn_getBitValue(isnull(DataByte,0),5)=0
)
go

if object_id('dbo.xp_insertObjectData') is not null
	drop procedure dbo.xp_insertObjectData
go
/*
Example:
	declare @EID int = 1
	declare @Keyword nvarchar(800)
	declare @JSON nvarchar(max)
	declare @Tokens nvarchar(max)
	exec dbo.xp_insertObjectData @EID, @Keyword, @JSON, @Tokens
Description :
	dbo.xp_insertObjectData，插入一筆資料
*/
create procedure dbo.xp_insertObjectData(
	@EID int,
	@Keyword nvarchar(800),
	@JSON nvarchar(max), -- {"google":[],"bing":[],"youtube":[],"yahoo":[],"all":[]}
	@Tokens nvarchar(max) -- N'a', N'b', N'c'
)
as 
begin
	begin try
		set nocount on
		declare @OID int, @nlevel int
		declare @CName nvarchar(800) = N'' + rtrim(ltrim(@Keyword))
		declare @CDes nvarchar(max) = rtrim(ltrim(@JSON))
		declare @sqlcmd nvarchar(max) = ''
	
		-- (1.) not exists -> insert or exists -> update
		if not exists( select * from Object where CName=@CName )
		begin
			insert into Object(Type,CName,CDes, nClick) values (@EID,@CName,@CDes,0)	
			select @OID = scope_identity()
		end
		else
		begin
			select @OID = OID, @nlevel = nClick from Object where Type = @EID and CName = @CName
			update Object set CDes = @CDes where OID = @OID
		end
		-- (2.) insert tokens, which are not in database 
		if object_id('tempdb..#tmp') is not null
    		drop table #tmp
		create table #tmp(
			CName nvarchar(800) not null
			constraint PK_#tmp_cname primary key clustered (CName)
		)
		set @sqlcmd = '
			insert into #tmp(CName) 
				select distinct rtrim(ltrim(CName)) from (values '+@Tokens+') f(CName)
		'
		exec (@sqlcmd)
		insert into Object(Type, CName, nClick)
			select distinct @EID, CName, isnull(@nlevel,0)+1
			from #tmp t 
			where not exists ( select * from Object o where o.Type = @EID and o.CName = t.CName )
		-- (3.) Create an association
		insert into ORel(OID1, OID2, Des)
			select distinct @OID, o.OID, 'suggest'
			from #tmp t, Object o
			where o.Type = @EID and t.CName = o.CName and not exists( select * from ORel where OID1 = @OID and OID2 = o.OID )
		delete from ORel where OID1 = OID2 and OID2 = OID1	
		-- (4.) Update Databyte Value
		update Object set DataByte = dbo.fn_updateBitValue(isnull(Databyte,0x0),5,1) where OID = @OID

		if object_id('tempdb..#tmp') is not null
    		drop table #tmp
		set nocount off
	end try
	begin catch
	--系統拋回訊息用
		DECLARE @ErrorMessage As VARCHAR(1000) = CHAR(10)+'錯誤代碼：' +CAST(ERROR_NUMBER() AS VARCHAR)
												+CHAR(10)+'錯誤訊息：'+	ERROR_MESSAGE()
												+CHAR(10)+'錯誤行號：'+	CAST(ERROR_LINE() AS VARCHAR)
												+CHAR(10)+'錯誤程序名稱：'+	ISNULL(ERROR_PROCEDURE(),'')
		DECLARE @ErrorSeverity As Numeric = ERROR_SEVERITY()
		DECLARE @ErrorState As Numeric = ERROR_STATE()
		RAISERROR( @ErrorMessage, @ErrorSeverity, @ErrorState);--回傳錯誤資訊
	end catch
	return
end
go