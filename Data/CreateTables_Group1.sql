USE MIST460_RDB_Group1;
GO


IF OBJECT_ID('GameGenre')       IS NOT NULL DROP TABLE GameGenre;
IF OBJECT_ID('PlayerStats')     IS NOT NULL DROP TABLE PlayerStats;
IF OBJECT_ID('GamerReview')     IS NOT NULL DROP TABLE GamerReview;
IF OBJECT_ID('Library')         IS NOT NULL DROP TABLE Library;
IF OBJECT_ID('Game')            IS NOT NULL DROP TABLE Game;
IF OBJECT_ID('Genre')           IS NOT NULL DROP TABLE Genre;
IF OBJECT_ID('Developer')       IS NOT NULL DROP TABLE Developer;
IF OBJECT_ID('Gamer')           IS NOT NULL DROP TABLE Gamer;
IF OBJECT_ID('AppUser')         IS NOT NULL DROP TABLE AppUser;
GO

-- ============================================================
-- AppUser (base/parent table -- Gamer and Developer inherit from this)
-- ============================================================

CREATE TABLE AppUser (
    AppUserID       INT IDENTITY(1,1)
        CONSTRAINT PK_AppUser PRIMARY KEY,
    FirstName       NVARCHAR(50)  NOT NULL,
    LastName        NVARCHAR(50)  NOT NULL,
    Phone           NVARCHAR(20)  NULL,
    Email           NVARCHAR(100) NOT NULL
        CONSTRAINT UK_AppUser_Email UNIQUE,
    PasswordHash    VARBINARY(256) NOT NULL,       -- store salted hash
    UserRole        NVARCHAR(20)  NOT NULL
        CONSTRAINT CK_AppUser_UserRole CHECK (UserRole IN (N'Gamer', N'Developer'))
);
GO

-- ============================================================
-- Gamer (kid of AppUser)
-- ============================================================

CREATE TABLE Gamer (
    GamerID                 INT
        CONSTRAINT PK_Gamer PRIMARY KEY
        CONSTRAINT FK_Gamer_AppUser FOREIGN KEY (GamerID)
            REFERENCES AppUser(AppUserID) ON DELETE CASCADE,
    PreferredGenres         NVARCHAR(200)   NULL,
    PreferredDifficulty     NVARCHAR(50)    NULL
        CONSTRAINT CK_Gamer_Difficulty CHECK (PreferredDifficulty IN (N'Easy', N'Medium', N'Hard', N'Expert', NULL)),
    PreferredPlayStyle      NVARCHAR(100)   NULL,
    PreferredMode           NVARCHAR(50)    NULL
        CONSTRAINT CK_Gamer_Mode CHECK (PreferredMode IN (N'Single-Player', N'Multiplayer', N'Co-op', NULL)),
    AvailablePlayTime       DECIMAL(5,2)    NULL    -- hours per week
        CONSTRAINT CK_Gamer_PlayTime CHECK (AvailablePlayTime >= 0)
);
GO

-- ============================================================
-- Developer (kid of AppUser)
-- ============================================================

CREATE TABLE Developer (
    DeveloperID     INT
        CONSTRAINT PK_Developer PRIMARY KEY
        CONSTRAINT FK_Developer_AppUser FOREIGN KEY (DeveloperID)
            REFERENCES AppUser(AppUserID) ON DELETE CASCADE,
    StudioName      NVARCHAR(200)   NOT NULL,
    StudioWebsite   NVARCHAR(300)   NULL
);
GO

-- ============================================================
-- Genre (lookup table)
-- ============================================================

CREATE TABLE Genre (
    GenreID     INT IDENTITY(1,1)
        CONSTRAINT PK_Genre PRIMARY KEY,
    GenreName   NVARCHAR(100) NOT NULL
        CONSTRAINT UK_Genre_Name UNIQUE
);
GO

-- ============================================================
-- Game
-- ============================================================

CREATE TABLE Game (
    GameID              INT IDENTITY(1,1)
        CONSTRAINT PK_Game PRIMARY KEY,
    DeveloperID         INT NOT NULL
        CONSTRAINT FK_Game_Developer FOREIGN KEY (DeveloperID)
            REFERENCES Developer(DeveloperID) ON DELETE NO ACTION,
    GameTitle           NVARCHAR(200)   NOT NULL,
    GameDescription     NVARCHAR(MAX)   NULL,
    YearReleased        INT             NULL
        CONSTRAINT CK_Game_Year CHECK (YearReleased >= 1970 AND YearReleased <= 2100),
    AverageRating       DECIMAL(4,2)    NOT NULL
        CONSTRAINT DF_Game_Rating DEFAULT (0.0)
        CONSTRAINT CK_Game_Rating CHECK (AverageRating >= 0 AND AverageRating <= 5)
);
GO

-- ============================================================
-- GameGenre (many-to-many: Game <-> Genre)
-- ============================================================

CREATE TABLE GameGenre (
    GameGenreID     INT IDENTITY(1,1)
        CONSTRAINT PK_GameGenre PRIMARY KEY,
    GameID          INT NOT NULL
        CONSTRAINT FK_GameGenre_Game FOREIGN KEY (GameID)
            REFERENCES Game(GameID) ON DELETE CASCADE,
    GenreID         INT NOT NULL
        CONSTRAINT FK_GameGenre_Genre FOREIGN KEY (GenreID) --NOTE : I am not sure here
            REFERENCES Genre(GenreID) ON DELETE CASCADE,
    CONSTRAINT UK_GameGenre UNIQUE (GameID, GenreID)
);
GO

-- ============================================================
-- Library (a Gamer's personal game collection: 0..1 per Gamer)
-- ============================================================

CREATE TABLE Library (
    LibraryID   INT IDENTITY(1,1)
        CONSTRAINT PK_Library PRIMARY KEY,
    GamerID     INT NOT NULL
        CONSTRAINT FK_Library_Gamer FOREIGN KEY (GamerID)
            REFERENCES Gamer(GamerID) ON DELETE CASCADE,
    GameID      INT NOT NULL
        CONSTRAINT FK_Library_Game FOREIGN KEY (GameID)
            REFERENCES Game(GameID) ON DELETE NO ACTION,
    DateAdded   DATETIME NOT NULL
        CONSTRAINT DF_Library_DateAdded DEFAULT (GETDATE()),
    CONSTRAINT UK_Library_GamerGame UNIQUE (GamerID, GameID)  -- a gamer can't add the same game twice
);
GO

-- ============================================================
-- PlayerStats (tracks a Gamer's stats for a specific Game,
--              linked through their Library  0..* per Library)
-- ============================================================

CREATE TABLE PlayerStats (
    PlayerStatsID   INT IDENTITY(1,1)
        CONSTRAINT PK_PlayerStats PRIMARY KEY,
    LibraryID       INT NOT NULL
        CONSTRAINT FK_PlayerStats_Library FOREIGN KEY (LibraryID)
            REFERENCES Library(LibraryID) ON DELETE CASCADE,
    GameID          INT NOT NULL
        CONSTRAINT FK_PlayerStats_Game FOREIGN KEY (GameID)
            REFERENCES Game(GameID) ON DELETE NO ACTION,
    HoursPlayed     DECIMAL(8,2) NOT NULL
        CONSTRAINT DF_PlayerStats_Hours DEFAULT (0.0)
        CONSTRAINT CK_PlayerStats_Hours CHECK (HoursPlayed >= 0),
    Status          NVARCHAR(30) NOT NULL
        CONSTRAINT DF_PlayerStats_Status DEFAULT (N'Not Started')
        CONSTRAINT CK_PlayerStats_Status CHECK (Status IN (N'Not Started', N'In Progress', N'Completed', N'Abandoned')),
    CONSTRAINT UK_PlayerStats_LibraryGame UNIQUE (LibraryID, GameID)
);
GO

-- ============================================================
-- GamerReview (a Gamer reviews a Game  0..* per Gamer, 0..* per Game)
-- ============================================================

CREATE TABLE GamerReview (
    GamerReviewID   INT IDENTITY(1,1)
        CONSTRAINT PK_GamerReview PRIMARY KEY,
    GamerID         INT NOT NULL
        CONSTRAINT FK_GamerReview_Gamer FOREIGN KEY (GamerID)
            REFERENCES Gamer(GamerID) ON DELETE CASCADE,
    GameID          INT NOT NULL
        CONSTRAINT FK_GamerReview_Game FOREIGN KEY (GameID)
            REFERENCES Game(GameID) ON DELETE NO ACTION,
    ReviewText      NVARCHAR(MAX)   NULL,
    Rating          DECIMAL(3,1)    NOT NULL
        CONSTRAINT CK_GamerReview_Rating CHECK (Rating >= 0 AND Rating <= 5),
    ReviewDate      DATETIME        NOT NULL
        CONSTRAINT DF_GamerReview_Date DEFAULT (GETDATE()),
    CONSTRAINT UK_GamerReview UNIQUE (GamerID, GameID)   -- one review per gamer per game
);
GO

