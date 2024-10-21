USE [ManageDevise]
GO
/****** Object:  Table [dbo].[DeviceChecks]    Script Date: 21/10/2024 5:22:37 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DeviceChecks](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Kernel] [varchar](255) NOT NULL,
	[av_check] [bit] NOT NULL,
	[dns_check] [bit] NOT NULL,
	[rdp_check] [bit] NOT NULL,
	[fw_check] [bit] NOT NULL,
	[Fecha_Generacion] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[DeviceChecks] ADD  DEFAULT (getdate()) FOR [Fecha_Generacion]
GO
/****** Object:  StoredProcedure [dbo].[InsertDeviceCheck]    Script Date: 21/10/2024 5:22:38 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[InsertDeviceCheck]
    @Kernel VARCHAR(255),
    @av_check BIT,
    @dns_check BIT,
    @rdp_check BIT,
    @fw_check BIT
AS
BEGIN
    INSERT INTO DeviceChecks (Kernel, av_check, dns_check, rdp_check, fw_check, Fecha_Generacion)
    VALUES (@Kernel, @av_check, @dns_check, @rdp_check, @fw_check, GETDATE());
END;
GO
