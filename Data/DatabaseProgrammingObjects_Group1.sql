--   Build small, focused objects and compose them into bigger
--   ones. 
--
-- DEPENDENCY LAYERS (bottom = must exist first):
--
--   LAYER 4: Stored Procedures (complex workflows)
--      calls Layer 3 procedures + Layer 1/2 functions
--         |
--   LAYER 3: Stored Procedures (single-purpose actions)
--      calls Layer 1 and Layer 2 functions
--         |
--   LAYER 2: Triggers
--      calls Layer 1 functions
--         |
--   LAYER 1: Functions (pure logic, no side effects)
--      called by everything above
--
-- CREATE ORDER:  Layer 1 → Layer 2 → Layer 3 → Layer 4
-- DROP ORDER:    Layer 4 → Layer 3 → Layer 2 → Layer 1
-- ============================================================

--USE mist460-api-group1;
GO



-- Layer 4: High-level orchestration procedures (call other procedures)
IF OBJECT_ID('sp_FullGamerOnboarding')      IS NOT NULL DROP PROCEDURE sp_FullGamerOnboarding;
IF OBJECT_ID('sp_GetDeveloperAnalytics')    IS NOT NULL DROP PROCEDURE sp_GetDeveloperAnalytics;
IF OBJECT_ID('sp_GetNextGameSuggestion')    IS NOT NULL DROP PROCEDURE sp_GetNextGameSuggestion;
GO

-- Layer 3: Single-action procedures (call functions)
IF OBJECT_ID('procValidateUser')            IS NOT NULL DROP PROCEDURE procValidateUser;
IF OBJECT_ID('sp_RegisterGamer')            IS NOT NULL DROP PROCEDURE sp_RegisterGamer;
IF OBJECT_ID('sp_AddGameToLibrary')         IS NOT NULL DROP PROCEDURE sp_AddGameToLibrary;
IF OBJECT_ID('sp_UpdateGameStatus')         IS NOT NULL DROP PROCEDURE sp_UpdateGameStatus;
IF OBJECT_ID('sp_SubmitReview')             IS NOT NULL DROP PROCEDURE sp_SubmitReview;
IF OBJECT_ID('sp_GetRecommendations')       IS NOT NULL DROP PROCEDURE sp_GetRecommendations;
IF OBJECT_ID('sp_SearchGamesByKeyword')     IS NOT NULL DROP PROCEDURE sp_SearchGamesByKeyword;
-- Guard procedures (called by other Layer 3 procs)
IF OBJECT_ID('sp_AssertGamerExists')        IS NOT NULL DROP PROCEDURE sp_AssertGamerExists;
IF OBJECT_ID('sp_ResolveGameID')            IS NOT NULL DROP PROCEDURE sp_ResolveGameID;
GO

-- Layer 2: Triggers (call Layer 1 functions)
IF OBJECT_ID('trg_GamerReview_RecalcRating')        IS NOT NULL DROP TRIGGER trg_GamerReview_RecalcRating;
IF OBJECT_ID('trg_PreventDuplicateLibraryEntry')    IS NOT NULL DROP TRIGGER trg_PreventDuplicateLibraryEntry;
IF OBJECT_ID('trg_AutoInitPlayerStats')             IS NOT NULL DROP TRIGGER trg_AutoInitPlayerStats;
IF OBJECT_ID('trg_BlockFinishedGameStatusChange')   IS NOT NULL DROP TRIGGER trg_BlockFinishedGameStatusChange;
GO

-- Layer 1: Functions (no dependencies — pure logic)
IF OBJECT_ID('fn_GetGamerLibrary')          IS NOT NULL DROP FUNCTION fn_GetGamerLibrary;
IF OBJECT_ID('fn_GetTotalHoursPlayed')      IS NOT NULL DROP FUNCTION fn_GetTotalHoursPlayed;
IF OBJECT_ID('fn_GetGameAverageRating')     IS NOT NULL DROP FUNCTION fn_GetGameAverageRating;
IF OBJECT_ID('fn_GetGameCompletionRate')    IS NOT NULL DROP FUNCTION fn_GetGameCompletionRate;
IF OBJECT_ID('fn_GetGamerCompletedCount')   IS NOT NULL DROP FUNCTION fn_GetGamerCompletedCount;
IF OBJECT_ID('fn_GetTopGenreForGame')       IS NOT NULL DROP FUNCTION fn_GetTopGenreForGame;
IF OBJECT_ID('fn_GamerOwnsGame')            IS NOT NULL DROP FUNCTION fn_GamerOwnsGame;
IF OBJECT_ID('fn_GamerAlreadyReviewed')     IS NOT NULL DROP FUNCTION fn_GamerAlreadyReviewed;
IF OBJECT_ID('fn_GamerExists')              IS NOT NULL DROP FUNCTION fn_GamerExists;
IF OBJECT_ID('fn_GameExists')               IS NOT NULL DROP FUNCTION fn_GameExists;
IF OBJECT_ID('fn_GetGameIDByTitle')         IS NOT NULL DROP FUNCTION fn_GetGameIDByTitle;
GO


-- ============================================================
-- ============================================================
--   LAYER 1: FUNCTIONS
--   Pure logic — no INSERT/UPDATE/DELETE allowed in functions.
--   Called by triggers, procedures, and other functions.
--   CREATE THESE FIRST.
-- ============================================================
-- ============================================================


-- ------------------------------------------------------------
-- fn_GamerExists  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_RegisterGamer, sp_AddGameToLibrary,
--            sp_GetRecommendations, sp_GetNextGameSuggestion
--
-- PURPOSE: Returns 1 if the GamerID exists, 0 if not.
--   Centralizes the existence check so every procedure
--   uses the exact same validation logic.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GamerExists (@GamerID INT)
RETURNS BIT
AS
BEGIN
    RETURN CASE
        WHEN EXISTS (SELECT 1 FROM Gamer WHERE GamerID = @GamerID)
        THEN 1 ELSE 0
    END;
END;
GO
-- USAGE: SELECT dbo.fn_GamerExists(1);   -- returns 1 (true) or 0 (false)


-- ------------------------------------------------------------
-- fn_GameExists  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_AddGameToLibrary, sp_SubmitReview,
--            sp_SearchGamesByKeyword
--
-- PURPOSE: Returns 1 if the GameID exists in the catalog.
--   Same pattern as fn_GamerExists — one place to change
--   if the Game table is ever renamed or restructured.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GameExists (@GameID INT)
RETURNS BIT
AS
BEGIN
    RETURN CASE
        WHEN EXISTS (SELECT 1 FROM Game WHERE GameID = @GameID)
        THEN 1 ELSE 0
    END;
END;
GO
-- USAGE: SELECT dbo.fn_GameExists(99);   -- returns 0 (not found)


-- ------------------------------------------------------------
-- fn_GetGameIDByTitle  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_AddGameToLibrary, sp_UpdateGameStatus,
--            sp_SubmitReview, sp_GetDeveloperAnalytics
--
-- PURPOSE: Resolves a game title to its GameID with a single
--   reusable lookup (case-insensitive, trims whitespace).
--   Returns one of three possible values so callers can raise
--   the appropriate error message:
--
--     * a positive INT  -> exactly one match (the GameID)
--     *  NULL           -> no game with that title
--     *  -1             -> multiple games share that title (ambiguous)
--
--   Centralizing this here means every procedure that accepts
--   a title parameter has identical lookup behavior.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetGameIDByTitle (@GameTitle NVARCHAR(200))
RETURNS INT
AS
BEGIN
    DECLARE @MatchCount INT;
    DECLARE @GameID     INT;

    SELECT @MatchCount = COUNT(*)
    FROM Game
    WHERE LTRIM(RTRIM(GameTitle)) = LTRIM(RTRIM(@GameTitle));

    IF @MatchCount = 0  RETURN NULL;
    IF @MatchCount > 1  RETURN -1;

    SELECT @GameID = GameID
    FROM Game
    WHERE LTRIM(RTRIM(GameTitle)) = LTRIM(RTRIM(@GameTitle));

    RETURN @GameID;
END;
GO
-- USAGE: SELECT dbo.fn_GetGameIDByTitle('Diablo IV');         -- returns 2
-- USAGE: SELECT dbo.fn_GetGameIDByTitle('Made-up Game');      -- returns NULL
-- USAGE: SELECT dbo.fn_GetGameIDByTitle('Duplicate Title');   -- returns -1


-- ------------------------------------------------------------
-- fn_GamerOwnsGame  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_AddGameToLibrary (duplicate check),
--            sp_SubmitReview (ownership check),
--            sp_UpdateGameStatus (library check),
--            trg_PreventDuplicateLibraryEntry
--
-- PURPOSE: Returns 1 if a gamer already has a game in their
--   library. Used both to PREVENT duplicates and to REQUIRE
--   ownership before reviewing.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GamerOwnsGame (@GamerID INT, @GameID INT)
RETURNS BIT
AS
BEGIN
    RETURN CASE
        WHEN EXISTS (
            SELECT 1 FROM Library
            WHERE GamerID = @GamerID AND GameID = @GameID
        )
        THEN 1 ELSE 0
    END;
END;
GO
-- USAGE: SELECT dbo.fn_GamerOwnsGame(1, 5);   -- 1=yes, 0=no


-- ------------------------------------------------------------
-- fn_GamerAlreadyReviewed  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_SubmitReview
--
-- PURPOSE: Returns 1 if the gamer has already submitted a
--   review for this game. Enforces the one-review-per-gamer
--   business rule in a reusable, readable way.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GamerAlreadyReviewed (@GamerID INT, @GameID INT)
RETURNS BIT
AS
BEGIN
    RETURN CASE
        WHEN EXISTS (
            SELECT 1 FROM GamerReview
            WHERE GamerID = @GamerID AND GameID = @GameID
        )
        THEN 1 ELSE 0
    END;
END;
GO
-- USAGE: SELECT dbo.fn_GamerAlreadyReviewed(1, 2);


-- ------------------------------------------------------------
-- fn_GetGameAverageRating  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: trg_AfterInsertReview, trg_AfterUpdateReview,
--            trg_AfterDeleteReview, sp_SubmitReview,
--            sp_GetDeveloperAnalytics
--
-- PURPOSE: Calculates the live average rating for a game
--   from GamerReview. This is the single source of truth
--   for all rating calculations across the entire system.
--   Change the formula here → updated everywhere automatically.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetGameAverageRating (@GameID INT)
RETURNS DECIMAL(4,2)
AS
BEGIN
    DECLARE @Avg DECIMAL(4,2);

    SELECT @Avg = AVG(Rating)
    FROM GamerReview
    WHERE GameID = @GameID;

    RETURN ISNULL(@Avg, 0.0);
END;
GO
-- USAGE: SELECT dbo.fn_GetGameAverageRating(1);


-- ------------------------------------------------------------
-- fn_GetGameCompletionRate  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_GetRecommendations, sp_SearchGamesByKeyword,
--            sp_GetDeveloperAnalytics
--
-- PURPOSE: Returns what % of owners have finished a game.
--   Used by developer analytics AND shown to players in
--   search results as a quality/difficulty signal.
--   (High completion = accessible, low = very hard or boring)
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetGameCompletionRate (@GameID INT)
RETURNS DECIMAL(5,2)
AS
BEGIN
    DECLARE @Owners   INT;
    DECLARE @Finished INT;

    SELECT @Owners = COUNT(DISTINCT l.GamerID)
    FROM Library l
    WHERE l.GameID = @GameID;

    SELECT @Finished = COUNT(DISTINCT l.GamerID)
    FROM Library l
        JOIN PlayerStats ps ON l.LibraryID = ps.LibraryID
    WHERE l.GameID  = @GameID
      AND ps.Status = N'Completed';

    IF @Owners = 0 RETURN 0.00;

    RETURN CAST(@Finished AS DECIMAL(10,2))
         / CAST(@Owners   AS DECIMAL(10,2)) * 100.0;
END;
GO
-- USAGE: SELECT dbo.fn_GetGameCompletionRate(1);


-- ------------------------------------------------------------
-- fn_GetTopGenreForGame  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: fn_GetGamerLibrary (table-valued function),
--            sp_GetRecommendations, sp_GetNextGameSuggestion,
--            sp_SearchGamesByKeyword
--
-- PURPOSE: Returns the primary genre label for a game.
--   Used as a display field in multiple result sets.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetTopGenreForGame (@GameID INT)
RETURNS NVARCHAR(100)
AS
BEGIN
    DECLARE @Genre NVARCHAR(100);

    SELECT TOP 1 @Genre = ge.GenreName
    FROM GameGenre gg
        JOIN Genre ge ON gg.GenreID = ge.GenreID
    WHERE gg.GameID = @GameID
    ORDER BY ge.GenreName ASC;

    RETURN ISNULL(@Genre, N'Unknown');
END;
GO
-- USAGE: SELECT dbo.fn_GetTopGenreForGame(1);


-- ------------------------------------------------------------
-- fn_GetTotalHoursPlayed  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_GetDeveloperAnalytics, sp_GetNextGameSuggestion
--
-- PURPOSE: Total hours a gamer has played across all games.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetTotalHoursPlayed (@GamerID INT)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @Total DECIMAL(10,2);

    SELECT @Total = SUM(ps.HoursPlayed)
    FROM PlayerStats ps
        JOIN Library l ON ps.LibraryID = l.LibraryID
    WHERE l.GamerID = @GamerID;

    RETURN ISNULL(@Total, 0.0);
END;
GO
-- USAGE: SELECT dbo.fn_GetTotalHoursPlayed(1);


-- ------------------------------------------------------------
-- fn_GetGamerCompletedCount  (Scalar)
-- ------------------------------------------------------------
-- REUSED BY: sp_GetNextGameSuggestion, sp_GetDeveloperAnalytics
--
-- PURPOSE: How many games this gamer has finished.
--   Used to personalize the next-game suggestion message
--   and to segment players in developer analytics.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetGamerCompletedCount (@GamerID INT)
RETURNS INT
AS
BEGIN
    DECLARE @Count INT;

    SELECT @Count = COUNT(*)
    FROM Library l
        JOIN PlayerStats ps ON l.LibraryID = ps.LibraryID
    WHERE l.GamerID = @GamerID
      AND ps.Status = N'Completed';

    RETURN ISNULL(@Count, 0);
END;
GO
-- USAGE: SELECT dbo.fn_GetGamerCompletedCount(1);


-- ------------------------------------------------------------
-- fn_GetGamerLibrary  (Table-Valued)
-- ------------------------------------------------------------
-- REUSED BY: sp_GetNextGameSuggestion, sp_GetDeveloperAnalytics
--
-- PURPOSE: Returns the full library for a gamer as a table.
--   Calling procedures JOIN or filter this result instead of
--   rewriting the same 4-table join every time.
--
-- NOTE: Calls fn_GetTopGenreForGame internally —
--   a function calling another function.
-- ------------------------------------------------------------
CREATE FUNCTION fn_GetGamerLibrary (@GamerID INT)
RETURNS TABLE
AS
RETURN
(
    SELECT
        ga.GameID,
        ga.GameTitle,
        ga.YearReleased,
        ga.AverageRating,
        -- calling another Layer 1 function from inside this function
        dbo.fn_GetTopGenreForGame(ga.GameID)   AS PrimaryGenre,
        ps.HoursPlayed,
        ps.Status,
        l.LibraryID,
        l.DateAdded
    FROM Library l
        JOIN Game ga             ON l.GameID    = ga.GameID
        LEFT JOIN PlayerStats ps ON l.LibraryID = ps.LibraryID
    WHERE l.GamerID = @GamerID
);
GO
-- USAGE: SELECT * FROM dbo.fn_GetGamerLibrary(1);
-- USAGE: SELECT * FROM dbo.fn_GetGamerLibrary(1) WHERE Status = 'Finished';


-- ============================================================
-- ============================================================
--   LAYER 2: TRIGGERS
--   Call Layer 1 functions.
--   CREATE AFTER Layer 1.
-- ============================================================
-- ============================================================


-- ------------------------------------------------------------
-- trg_GamerReview_RecalcRating
-- ------------------------------------------------------------
-- CALLS: fn_GetGameAverageRating (Layer 1)
--
-- PURPOSE: Single trigger that recalculates Game.AverageRating
--   whenever a review is inserted, updated, or deleted.
--   (Replaces three separate triggers — same logic, one place.)
--
-- The union of inserted+deleted covers every affected GameID:
--   INSERT     -> only inserted has rows
--   DELETE     -> only deleted has rows
--   UPDATE     -> both have rows (same GameID, different Rating)
-- ------------------------------------------------------------
CREATE TRIGGER trg_GamerReview_RecalcRating
ON GamerReview
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Game
    SET AverageRating = ISNULL(dbo.fn_GetGameAverageRating(Game.GameID), 0.0)
    WHERE Game.GameID IN (
        SELECT GameID FROM inserted
        UNION
        SELECT GameID FROM deleted
    );
END;
GO


-- ------------------------------------------------------------
-- trg_PreventDuplicateLibraryEntry
-- ------------------------------------------------------------
-- CALLS: fn_GamerOwnsGame (Layer 1)
--
-- PURPOSE: Intercepts INSERT on Library and uses the shared
--   fn_GamerOwnsGame check — the same check used by
--   sp_AddGameToLibrary — ensuring consistent duplicate
--   detection at both the procedure and trigger level.
-- ------------------------------------------------------------
CREATE TRIGGER trg_PreventDuplicateLibraryEntry
ON Library
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Reuse Layer 1 function instead of writing the EXISTS check again
    IF EXISTS (
        SELECT 1 FROM inserted i
        WHERE dbo.fn_GamerOwnsGame(i.GamerID, i.GameID) = 1
    )
    BEGIN
        RAISERROR('This game already exists in the gamer''s library.', 16, 1);
        RETURN;
    END

    INSERT INTO Library (GamerID, GameID, DateAdded)
    SELECT GamerID, GameID, DateAdded FROM inserted;
END;
GO


-- ------------------------------------------------------------
-- trg_AutoInitPlayerStats
-- ------------------------------------------------------------
-- CALLS: (no function needed — simple insert)
--
-- PURPOSE: Safety net that auto-creates a PlayerStats row
--   for every new Library entry even if inserted directly,
--   bypassing sp_AddGameToLibrary.
-- ------------------------------------------------------------
CREATE TRIGGER trg_AutoInitPlayerStats
ON Library
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO PlayerStats (LibraryID, HoursPlayed, Status)
    SELECT i.LibraryID, 0.0, N'Not Started'
    FROM inserted i
    WHERE NOT EXISTS (
        SELECT 1 FROM PlayerStats ps WHERE ps.LibraryID = i.LibraryID
    );
END;
GO


-- ------------------------------------------------------------
-- trg_BlockFinishedGameStatusChange
-- ------------------------------------------------------------
-- CALLS: (no function — direct comparison)
--
-- PURPOSE: Database-level guard preventing a 'Finished' status
--   from being rolled back. Works alongside the same check
--   inside sp_UpdateGameStatus (two layers of protection).
-- ------------------------------------------------------------
CREATE TRIGGER trg_BlockFinishedGameStatusChange
ON PlayerStats
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(Status)
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM deleted d
                JOIN inserted i ON d.PlayerStatsID = i.PlayerStatsID
            WHERE d.Status = N'Completed'
              AND i.Status IN (N'Not Started', N'In Progress')
        )
        BEGIN
            RAISERROR('A finished game cannot be rolled back to an earlier status.', 16, 1);
            ROLLBACK TRANSACTION;
        END
    END
END;
GO


-- ============================================================
-- ============================================================
--   LAYER 3: STORED PROCEDURES (single-purpose actions)
--   Call Layer 1 functions.
--   Called by Layer 4 orchestration procedures.
--   CREATE AFTER Layer 1 and Layer 2.
-- ============================================================
-- ============================================================


-- ============================================================
-- LAYER 3a: GUARD PROCEDURES
-- Tiny procs that wrap a check + THROW so callers can replace
-- repeated 5- to 13-line validation blocks with a single EXEC.
-- ============================================================


-- ------------------------------------------------------------
-- sp_AssertGamerExists
-- ------------------------------------------------------------
-- CALLS:    fn_GamerExists (Layer 1)
-- CALLED BY: sp_AddGameToLibrary, sp_GetRecommendations,
--            sp_GetNextGameSuggestion
--
-- PURPOSE: Throws "Gamer not found." when the GamerID does not
--   exist. Replaces a 5-line IF/RAISERROR/RETURN block in every
--   procedure that needs the check.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_AssertGamerExists
    @GamerID INT
AS
BEGIN
    SET NOCOUNT ON;
    IF dbo.fn_GamerExists(@GamerID) = 0
        THROW 50001, 'Gamer not found.', 1;
END;
GO
-- USAGE: EXEC sp_AssertGamerExists @GamerID = 1;


-- ------------------------------------------------------------
-- sp_ResolveGameID
-- ------------------------------------------------------------
-- CALLS:    fn_GetGameIDByTitle (Layer 1)
-- CALLED BY: sp_AddGameToLibrary, sp_UpdateGameStatus,
--            sp_SubmitReview, sp_GetDeveloperAnalytics
--
-- PURPOSE: Resolves a title to a GameID and throws a clear
--   error for the no-match / ambiguous-match cases. Callers
--   replace ~13 lines of branching with one EXEC.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_ResolveGameID
    @GameTitle  NVARCHAR(200),
    @GameID     INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    SET @GameID = dbo.fn_GetGameIDByTitle(@GameTitle);

    IF @GameID IS NULL
        THROW 50002, 'Game not found in catalog. Check the title and try again.', 1;
    IF @GameID = -1
        THROW 50003, 'Multiple games share that title — please be more specific.', 1;
END;
GO
-- USAGE: DECLARE @id INT;
--        EXEC sp_ResolveGameID @GameTitle='Diablo IV', @GameID=@id OUTPUT;


-- ------------------------------------------------------------
-- procValidateUser
-- ------------------------------------------------------------
-- CALLS:    (none — direct lookup)
-- CALLED BY: API /validate_user/ endpoint
--
-- PURPOSE: Authenticates a user by email + password.
--   Returns AppUserID and Fullname when credentials match,
--   or no rows when they don't. Used by the login screen.
-- ------------------------------------------------------------
CREATE PROCEDURE procValidateUser
    @username   NVARCHAR(100),   -- email is the login identifier
    @password   NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        AppUserID,
        FirstName + N' ' + LastName AS Fullname,
        UserRole
    FROM AppUser
    WHERE Email = @username
      AND PasswordHash = HASHBYTES('SHA2_256', @password);
END;
GO
-- USAGE: EXEC procValidateUser @username='alex.rivera@email.com', @password='alex123';


-- ------------------------------------------------------------
-- sp_RegisterGamer
-- ------------------------------------------------------------
-- CALLS:    fn_GamerExists (Layer 1) — for validation
-- CALLED BY: sp_FullGamerOnboarding (Layer 4)
--
-- PURPOSE: Creates AppUser + Gamer in one transaction.
--   Kept focused on just registration — onboarding
--   logic (adding starter games, etc.) lives in Layer 4.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_RegisterGamer
    @FirstName              NVARCHAR(50),
    @LastName               NVARCHAR(50),
    @Email                  NVARCHAR(100),
    @PasswordHash           VARBINARY(256),
    @Phone                  NVARCHAR(20)    = NULL,
    @PreferredGenres        NVARCHAR(200)   = NULL,
    @PreferredDifficulty    NVARCHAR(50)    = NULL,
    @PreferredPlayStyle     NVARCHAR(100)   = NULL,
    @PreferredMode          NVARCHAR(50)    = NULL,
    @AvailablePlayTime      DECIMAL(5,2)    = NULL,
    @NewGamerID             INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate email uniqueness (direct check — fn_GamerExists checks by ID not email)
    IF EXISTS (SELECT 1 FROM AppUser WHERE Email = @Email)
    BEGIN
        RAISERROR('An account with this email already exists.', 16, 1);
        RETURN;
    END

    BEGIN TRANSACTION;
    BEGIN TRY

        INSERT INTO AppUser (FirstName, LastName, Phone, Email, PasswordHash, UserRole)
        VALUES (@FirstName, @LastName, @Phone, @Email, @PasswordHash, N'Gamer');

        SET @NewGamerID = SCOPE_IDENTITY();

        INSERT INTO Gamer (GamerID, PreferredGenres, PreferredDifficulty,
                           PreferredPlayStyle, PreferredMode, AvailablePlayTime)
        VALUES (@NewGamerID, @PreferredGenres, @PreferredDifficulty,
                @PreferredPlayStyle, @PreferredMode, @AvailablePlayTime);

        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO
-- USAGE:
-- DECLARE @ID INT;
-- EXEC sp_RegisterGamer
--     @FirstName='Alex', @LastName='Rivera',
--     @Email='alex@email.com',
--     @PasswordHash=HASHBYTES('SHA2_256', N'alex123'),
--     @PreferredGenres='Action, First-Person Shooter', @PreferredDifficulty='Hard',
--     @NewGamerID=@ID OUTPUT;
-- SELECT @ID;


-- ------------------------------------------------------------
-- sp_AddGameToLibrary
-- ------------------------------------------------------------
-- CALLS:    fn_GamerExists (Layer 1)
--           fn_GameExists  (Layer 1)
--           fn_GamerOwnsGame (Layer 1)
-- CALLED BY: sp_FullGamerOnboarding (Layer 4)
--
-- PURPOSE: Adds a game to a gamer's library + initializes
--   PlayerStats. Uses Layer 1 functions for all validations
--   so the same rules apply whether called directly or from
--   the onboarding procedure.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_AddGameToLibrary
    @GamerID    INT,
    @GameTitle  NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;

    EXEC sp_AssertGamerExists @GamerID;

    DECLARE @GameID INT;
    EXEC sp_ResolveGameID @GameTitle = @GameTitle, @GameID = @GameID OUTPUT;

    IF dbo.fn_GamerOwnsGame(@GamerID, @GameID) = 1
    BEGIN
        RAISERROR('This game is already in the gamer''s library.', 16, 1);
        RETURN;
    END

    BEGIN TRANSACTION;
    BEGIN TRY
        DECLARE @NewLibraryID INT;

        INSERT INTO Library (GamerID, GameID, DateAdded)
        VALUES (@GamerID, @GameID, GETDATE());

        SET @NewLibraryID = SCOPE_IDENTITY();

        -- trg_AutoInitPlayerStats will also handle this as a safety net
        INSERT INTO PlayerStats (LibraryID, HoursPlayed, Status)
        VALUES (@NewLibraryID, 0.0, N'Not Started');

        COMMIT TRANSACTION;

        SELECT @NewLibraryID AS NewLibraryID;

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO
-- USAGE: EXEC sp_AddGameToLibrary @GamerID=1, @GameTitle='Diablo IV';


-- ------------------------------------------------------------
-- sp_UpdateGameStatus
-- ------------------------------------------------------------
-- CALLS:    fn_GamerOwnsGame (Layer 1) — to verify ownership
-- CALLED BY: sp_FullGamerOnboarding (Layer 4) — to set initial status
--
-- PURPOSE: Updates a game's play status and optionally hours.
--   The Finished rollback guard is enforced both here AND
--   by trg_BlockFinishedGameStatusChange (two layers).
-- ------------------------------------------------------------
CREATE PROCEDURE sp_UpdateGameStatus
    @GamerID        INT,
    @GameTitle      NVARCHAR(200),
    @NewStatus      NVARCHAR(30),
    @HoursPlayed    DECIMAL(8,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @GameID INT;
    EXEC sp_ResolveGameID @GameTitle = @GameTitle, @GameID = @GameID OUTPUT;

    -- Use Layer 1 function for ownership check
    IF dbo.fn_GamerOwnsGame(@GamerID, @GameID) = 0
    BEGIN
        RAISERROR('This game is not in the gamer''s library.', 16, 1);
        RETURN;
    END

    DECLARE @LibraryID  INT;
    DECLARE @OldStatus  NVARCHAR(30);

    SELECT  @LibraryID = l.LibraryID,
            @OldStatus = ps.Status
    FROM Library l
        JOIN PlayerStats ps ON l.LibraryID = ps.LibraryID
    WHERE l.GamerID = @GamerID AND l.GameID = @GameID;

    -- Guard: cannot roll back a Finished game
    IF @OldStatus = N'Completed' AND @NewStatus IN (N'Not Started', N'In Progress')
    BEGIN
        RAISERROR('A finished game cannot be set back to an earlier status.', 16, 1);
        RETURN;
    END

    UPDATE PlayerStats
    SET
        Status      = @NewStatus,
        HoursPlayed = CASE WHEN @HoursPlayed IS NOT NULL
                          THEN @HoursPlayed ELSE HoursPlayed END
    WHERE LibraryID = @LibraryID;

    -- Return confirmation using the Layer 1 table-valued function
    SELECT GameTitle, PrimaryGenre, Status, HoursPlayed
    FROM dbo.fn_GetGamerLibrary(@GamerID)
    WHERE GameID = @GameID;

END;
GO
-- USAGE: EXEC sp_UpdateGameStatus @GamerID=1, @GameTitle='Call of Duty: Modern Warfare III', @NewStatus='In Progress', @HoursPlayed=12.5;


-- ------------------------------------------------------------
-- sp_SubmitReview
-- ------------------------------------------------------------
-- CALLS:    fn_GamerOwnsGame       (Layer 1) — ownership check
--           fn_GamerAlreadyReviewed (Layer 1) — duplicate check
--           fn_GetGameAverageRating (Layer 1) — rating update
-- CALLED BY: sp_FullGamerOnboarding (Layer 4) — optional review on onboard
--
-- PURPOSE: Submits a review + recalculates AverageRating.
--   All business rule checks are delegated to Layer 1 functions.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_SubmitReview
    @GamerID    INT,
    @GameTitle  NVARCHAR(200),
    @Rating     DECIMAL(3,1),
    @ReviewText NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @GameID INT;
    EXEC sp_ResolveGameID @GameTitle = @GameTitle, @GameID = @GameID OUTPUT;

    -- Both validations use Layer 1 functions
    IF dbo.fn_GamerOwnsGame(@GamerID, @GameID) = 0
    BEGIN
        RAISERROR('You must own the game before submitting a review.', 16, 1);
        RETURN;
    END

    IF dbo.fn_GamerAlreadyReviewed(@GamerID, @GameID) = 1
    BEGIN
        RAISERROR('You have already reviewed this game.', 16, 1);
        RETURN;
    END

    BEGIN TRANSACTION;
    BEGIN TRY

        INSERT INTO GamerReview (GamerID, GameID, ReviewText, Rating, ReviewDate)
        VALUES (@GamerID, @GameID, @ReviewText, @Rating, GETDATE());

        -- Layer 1 function recalculates the rating
        -- (trg_AfterInsertReview also does this as a safety net)
        UPDATE Game
        SET AverageRating = dbo.fn_GetGameAverageRating(@GameID)
        WHERE GameID = @GameID;

        COMMIT TRANSACTION;

        SELECT GameTitle, AverageRating AS UpdatedAvgRating
        FROM Game WHERE GameID = @GameID;

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO
-- USAGE: EXEC sp_SubmitReview @GamerID=1, @GameTitle='Diablo IV', @Rating=4.5, @ReviewText='Amazing!';


-- ------------------------------------------------------------
-- sp_GetRecommendations
-- ------------------------------------------------------------
-- CALLS:    fn_GamerExists          (Layer 1)
--           fn_GamerOwnsGame        (Layer 1) — to exclude owned games
--           fn_GetTopGenreForGame   (Layer 1)
--           fn_GetGameCompletionRate (Layer 1) — shown as quality signal
-- CALLED BY: sp_GetNextGameSuggestion (Layer 4) as fallback
--
-- PURPOSE: Core recommendation engine — returns top N unowned
--   games matching the gamer's preferences, ranked by rating.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_GetRecommendations
    @GamerID    INT,
    @TopN       INT = 6
AS
BEGIN
    SET NOCOUNT ON;

    EXEC sp_AssertGamerExists @GamerID;

    DECLARE @PreferredGenres NVARCHAR(200);

    SELECT @PreferredGenres = PreferredGenres
    FROM Gamer WHERE GamerID = @GamerID;

    -- Normalize the gamer's preferred genres into a proper list
    -- (split on commas, trim, drop empties) so we can match by exact
    -- genre name instead of fragile substring LIKE.
    DECLARE @PrefList TABLE (GenreName NVARCHAR(100) PRIMARY KEY);

    IF @PreferredGenres IS NOT NULL
    BEGIN
        INSERT INTO @PrefList (GenreName)
        SELECT DISTINCT LTRIM(RTRIM(value))
        FROM STRING_SPLIT(@PreferredGenres, ',')
        WHERE LTRIM(RTRIM(value)) <> N'';
    END

    -- Find unowned games that match at least one preferred genre.
    -- DISTINCT on GameID prevents the GameGenre join from returning
    -- the same game multiple times when it matches multiple genres.
    DECLARE @Matched TABLE (GameID INT PRIMARY KEY);

    INSERT INTO @Matched (GameID)
    SELECT DISTINCT g.GameID
    FROM Game g
        JOIN GameGenre gg ON g.GameID    = gg.GameID
        JOIN Genre ge     ON gg.GenreID  = ge.GenreID
        JOIN @PrefList p  ON p.GenreName = ge.GenreName
    WHERE dbo.fn_GamerOwnsGame(@GamerID, g.GameID) = 0;

    IF EXISTS (SELECT 1 FROM @Matched)
    BEGIN
        SELECT TOP (@TopN)
            g.GameID,
            g.GameTitle,
            g.YearReleased,
            g.AverageRating,
            d.StudioName,
            dbo.fn_GetTopGenreForGame(g.GameID)      AS PrimaryGenre,
            dbo.fn_GetGameCompletionRate(g.GameID)   AS CommunityCompletionPct,
            'Matches your preferences'               AS RecommendationReason
        FROM Game g
            JOIN Developer d ON g.DeveloperID = d.DeveloperID
            JOIN @Matched m  ON g.GameID      = m.GameID
        ORDER BY g.AverageRating DESC;

        RETURN;
    END

    -- Fallback: no genre match (or no preferences set) — return the
    -- top-rated unowned games so the caller always gets results.
    SELECT TOP (@TopN)
        g.GameID,
        g.GameTitle,
        g.YearReleased,
        g.AverageRating,
        d.StudioName,
        dbo.fn_GetTopGenreForGame(g.GameID)      AS PrimaryGenre,
        dbo.fn_GetGameCompletionRate(g.GameID)   AS CommunityCompletionPct,
        'Top-rated pick we think you''ll enjoy'  AS RecommendationReason
    FROM Game g
        JOIN Developer d ON g.DeveloperID = d.DeveloperID
    WHERE dbo.fn_GamerOwnsGame(@GamerID, g.GameID) = 0
    ORDER BY g.AverageRating DESC;

END;
GO
-- USAGE: EXEC sp_GetRecommendations @GamerID=1;
-- USAGE: EXEC sp_GetRecommendations @GamerID=1, @TopN=3;


-- ------------------------------------------------------------
-- sp_SearchGamesByKeyword
-- ------------------------------------------------------------
-- CALLS:    fn_GamerOwnsGame        (Layer 1) — flags owned games
--           fn_GetTopGenreForGame   (Layer 1)
--           fn_GetGameCompletionRate (Layer 1)
--
-- PURPOSE: Keyword search across title, description, genre.
--   Uses Layer 1 functions to enrich each result row.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_SearchGamesByKeyword
    @Keyword    NVARCHAR(200),
    @GamerID    INT  = NULL,
    @TopN       INT  = 10
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@TopN)
        g.GameID,
        g.GameTitle,
        g.GameDescription,
        g.YearReleased,
        g.AverageRating,
        d.StudioName,
        dbo.fn_GetTopGenreForGame(g.GameID)      AS PrimaryGenre,
        dbo.fn_GetGameCompletionRate(g.GameID)   AS CompletionRatePct,
        -- Use Layer 1 function to flag whether gamer already owns it
        CASE WHEN @GamerID IS NOT NULL
                  AND dbo.fn_GamerOwnsGame(@GamerID, g.GameID) = 1
             THEN 'Yes' ELSE 'No'
        END AS AlreadyOwned
    FROM Game g
        JOIN Developer d  ON g.DeveloperID = d.DeveloperID
        JOIN GameGenre gg ON g.GameID      = gg.GameID
        JOIN Genre ge     ON gg.GenreID    = ge.GenreID
    WHERE
        g.GameTitle          LIKE '%' + @Keyword + '%'
        OR g.GameDescription LIKE '%' + @Keyword + '%'
        OR d.StudioName      LIKE '%' + @Keyword + '%'
        OR ge.GenreName      LIKE '%' + @Keyword + '%'
    GROUP BY
        g.GameID, g.GameTitle, g.GameDescription,
        g.YearReleased, g.AverageRating, d.StudioName
    ORDER BY g.AverageRating DESC;
END;
GO
-- USAGE: EXEC sp_SearchGamesByKeyword @Keyword='open world', @GamerID=1;
--EXEC sp_GetRecommendations @GamerID = 1, @TopN = 6;
-- ------------------------------------------------------------
-- sp_GetDeveloperAnalytics
-- ------------------------------------------------------------
-- CALLS:    fn_GetGameAverageRating  (Layer 1)
--           fn_GetGameCompletionRate (Layer 1)
--           fn_GetGamerCompletedCount (Layer 1)
--
-- PURPOSE: Full analytics dashboard for developers.
--   Returns 3 result sets: summary, sentiment, player profile.
--   All metrics come from Layer 1 functions — change the
--   formula in one function and all analytics update.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_GetDeveloperAnalytics
    @GameTitle      NVARCHAR(200),
    @DeveloperID    INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @GameID INT;
    EXEC sp_ResolveGameID @GameTitle = @GameTitle, @GameID = @GameID OUTPUT;

    -- Security: developer can only see analytics for games they own
    IF NOT EXISTS (
        SELECT 1 FROM Game
        WHERE GameID = @GameID AND DeveloperID = @DeveloperID
    )
    BEGIN
        RAISERROR('Access denied — this game is not in your catalog.', 16, 1);
        RETURN;
    END

    -- ── RESULT SET 1: Performance Summary ───────────────────
    SELECT
        g.GameTitle,
        g.YearReleased,
        -- Layer 1 function for live rating
        dbo.fn_GetGameAverageRating(@GameID)        AS LiveAverageRating,
        -- Layer 1 function for completion rate
        dbo.fn_GetGameCompletionRate(@GameID)        AS CompletionRatePct,
        COUNT(DISTINCT l.GamerID)                    AS TotalOwners,
        SUM(CASE WHEN ps.Status = N'Completed'    THEN 1 ELSE 0 END) AS TotalFinished,
        SUM(CASE WHEN ps.Status = N'In Progress' THEN 1 ELSE 0 END) AS CurrentlyPlaying,
        SUM(CASE WHEN ps.Status = N'Not Started' THEN 1 ELSE 0 END) AS NotStarted,
        AVG(ps.HoursPlayed)                          AS AvgHoursPlayed,
        COUNT(DISTINCT gr.GamerReviewID)             AS TotalReviews
    FROM Game g
        LEFT JOIN Library l      ON g.GameID    = l.GameID
        LEFT JOIN PlayerStats ps ON l.LibraryID = ps.LibraryID
        LEFT JOIN GamerReview gr ON g.GameID    = gr.GameID
    WHERE g.GameID = @GameID
    GROUP BY g.GameTitle, g.YearReleased;

    -- ── RESULT SET 2: Review Sentiment ──────────────────────
    -- CTE assigns the sentiment bucket once so the GROUP BY
    -- doesn't have to repeat the CASE expression.
    WITH BucketedReviews AS (
        SELECT
            CASE
                WHEN Rating >= 4.0 THEN 'Positive (4.0 - 5.0)'
                WHEN Rating >= 2.5 THEN 'Mixed (2.5 - 3.9)'
                ELSE                    'Negative (0.0 - 2.4)'
            END AS SentimentBucket,
            Rating
        FROM GamerReview
        WHERE GameID = @GameID
    )
    SELECT
        SentimentBucket,
        COUNT(*)        AS ReviewCount,
        AVG(Rating)     AS AvgRating
    FROM BucketedReviews
    GROUP BY SentimentBucket
    ORDER BY AvgRating DESC;

    -- ── RESULT SET 3: Player Profile ────────────────────────
    SELECT
        ga.PreferredMode,
        ga.PreferredDifficulty,
        ga.PreferredPlayStyle,
        COUNT(*)                AS PlayerCount,
        AVG(ps.HoursPlayed)     AS AvgHoursPlayed,
        -- Layer 1 function per player to show their finished game count
        -- (segments casual vs dedicated players)
        AVG(CAST(dbo.fn_GetGamerCompletedCount(ga.GamerID) AS DECIMAL)) AS AvgGamesFinishedByThisPlayerType
    FROM Library l
        JOIN PlayerStats ps ON l.LibraryID = ps.LibraryID
        JOIN Gamer ga       ON l.GamerID   = ga.GamerID
    WHERE l.GameID = @GameID
    GROUP BY ga.PreferredMode, ga.PreferredDifficulty, ga.PreferredPlayStyle
    ORDER BY PlayerCount DESC;

END;
GO
-- USAGE: EXEC sp_GetDeveloperAnalytics @GameTitle='Echoes of Aether', @DeveloperID=6;


-- ============================================================
-- ============================================================
--   LAYER 4: ORCHESTRATION STORED PROCEDURES
--   Call Layer 3 procedures to coordinate multi-step workflows.
--   These are the highest-level objects in the system.
--   CREATE LAST.
-- ============================================================
-- ============================================================


-- ------------------------------------------------------------
-- sp_GetNextGameSuggestion
-- ------------------------------------------------------------
-- CALLS:    fn_GamerExists          (Layer 1)
--           fn_GetGamerCompletedCount (Layer 1)
--           fn_GetGamerLibrary      (Layer 1) — table-valued
--           sp_GetRecommendations   (Layer 3) — as fallback
--
-- PURPOSE: Suggests what game to play next.
--   Priority 1: Unstarted games from library
--   Priority 2: In Progress games to resume
--   Priority 3: Calls sp_GetRecommendations for new catalog games
--
-- This is a Layer 4 procedure because it calls both Layer 1
--   functions AND a Layer 3 procedure (sp_GetRecommendations).
-- ------------------------------------------------------------
CREATE PROCEDURE sp_GetNextGameSuggestion
    @GamerID INT
AS
BEGIN
    SET NOCOUNT ON;

    EXEC sp_AssertGamerExists @GamerID;

    -- Layer 1 function to count finished games for the suggestion message
    DECLARE @CompletedCount INT = dbo.fn_GetGamerCompletedCount(@GamerID);

    -- PRIORITY 1: Use Layer 1 table-valued function to check for unstarted games
    IF EXISTS (
        SELECT 1 FROM dbo.fn_GetGamerLibrary(@GamerID) WHERE Status = N'Not Started'
    )
    BEGIN
        SELECT TOP 1
            GameID, GameTitle, AverageRating, PrimaryGenre,
            Status, HoursPlayed,
            'You own this but have not started it yet'  AS SuggestionReason,
            @CompletedCount                             AS GamesYouHaveFinished
        FROM dbo.fn_GetGamerLibrary(@GamerID)       -- Layer 1 table-valued function
        WHERE Status = N'Not Started'
        ORDER BY AverageRating DESC;
        RETURN;
    END

    -- PRIORITY 2: Resume an in-progress game (also using Layer 1 TVF)
    IF EXISTS (
        SELECT 1 FROM dbo.fn_GetGamerLibrary(@GamerID) WHERE Status = N'In Progress'
    )
    BEGIN
        SELECT TOP 1
            GameID, GameTitle, AverageRating, PrimaryGenre,
            Status, HoursPlayed,
            'Resume this — you have ' + CAST(HoursPlayed AS NVARCHAR) + ' hours in it' AS SuggestionReason,
            @CompletedCount AS GamesYouHaveFinished
        FROM dbo.fn_GetGamerLibrary(@GamerID)       -- Layer 1 table-valued function
        WHERE Status = N'In Progress'
        ORDER BY HoursPlayed DESC;
        RETURN;
    END

    -- PRIORITY 3: All games done — call Layer 3 procedure for new recommendations
    -- This is what makes sp_GetNextGameSuggestion a Layer 4 procedure
    PRINT 'You have finished all your games! Here are some new recommendations:';
    EXEC sp_GetRecommendations @GamerID = @GamerID, @TopN = 3;  -- calling Layer 3

END;
GO
-- USAGE: EXEC sp_GetNextGameSuggestion @GamerID=2;


-- ------------------------------------------------------------
-- sp_FullGamerOnboarding
-- ------------------------------------------------------------
-- CALLS:    sp_RegisterGamer     (Layer 3)
--           sp_AddGameToLibrary  (Layer 3)
--           sp_GetRecommendations (Layer 3)
--
-- PURPOSE: The complete new-player onboarding workflow in
--   one call. Registers the gamer, adds any games they already
--   own, then immediately returns their first recommendations.
--
-- This is the highest-level object in the system.
--   It orchestrates three Layer 3 procedures in sequence,
--   wrapped in one transaction so if any step fails,
--   the entire onboarding is rolled back cleanly.
-- ------------------------------------------------------------
CREATE PROCEDURE sp_FullGamerOnboarding
    -- Registration fields (passed to sp_RegisterGamer)
    @FirstName              NVARCHAR(50),
    @LastName               NVARCHAR(50),
    @Email                  NVARCHAR(100),
    @PasswordHash           VARBINARY(256),
    @Phone                  NVARCHAR(20)    = NULL,
    @PreferredGenres        NVARCHAR(200)   = NULL,
    @PreferredDifficulty    NVARCHAR(50)    = NULL,
    @PreferredPlayStyle     NVARCHAR(100)   = NULL,
    @PreferredMode          NVARCHAR(50)    = NULL,
    @AvailablePlayTime      DECIMAL(5,2)    = NULL,
    -- Optional: pipe-separated Game Titles the gamer already owns
    -- e.g. 'Diablo IV|Far Cry 6|EA Sports FC 25'
    -- (pipe is used instead of comma because some game titles contain commas)
    @OwnedGameTitles        NVARCHAR(2000)  = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @NewGamerID INT;

    BEGIN TRANSACTION;
    BEGIN TRY

        -- STEP 1: Register the gamer by calling the Layer 3 procedure
        EXEC sp_RegisterGamer
            @FirstName           = @FirstName,
            @LastName            = @LastName,
            @Email               = @Email,
            @PasswordHash        = @PasswordHash,
            @Phone               = @Phone,
            @PreferredGenres     = @PreferredGenres,
            @PreferredDifficulty = @PreferredDifficulty,
            @PreferredPlayStyle  = @PreferredPlayStyle,
            @PreferredMode       = @PreferredMode,
            @AvailablePlayTime   = @AvailablePlayTime,
            @NewGamerID          = @NewGamerID OUTPUT;

        -- STEP 2: If the gamer already owns games, add them to their library
        -- Parse the pipe-separated list of titles and call sp_AddGameToLibrary for each
        IF @OwnedGameTitles IS NOT NULL
        BEGIN
            DECLARE @Pos        INT = 1;
            DECLARE @Remaining  NVARCHAR(2000) = @OwnedGameTitles + N'|';
            DECLARE @NextPipe   INT;
            DECLARE @Title      NVARCHAR(200);

            WHILE @Pos <= LEN(@Remaining)
            BEGIN
                SET @NextPipe = CHARINDEX(N'|', @Remaining, @Pos);
                IF @NextPipe = 0 BREAK;

                SET @Title = LTRIM(RTRIM(SUBSTRING(@Remaining, @Pos, @NextPipe - @Pos)));

                -- Call the Layer 3 procedure for each non-empty title
                IF LEN(@Title) > 0
                    EXEC sp_AddGameToLibrary
                        @GamerID   = @NewGamerID,
                        @GameTitle = @Title;

                SET @Pos = @NextPipe + 1;
            END
        END

        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;   -- undo registration AND all library adds
        THROW;
    END CATCH

    -- STEP 3: After committing, return first recommendations
    -- Called outside the transaction — read-only, no rollback needed
    PRINT 'Welcome! Here are your first game recommendations:';
    EXEC sp_GetRecommendations              -- calling Layer 3
        @GamerID = @NewGamerID,
        @TopN    = 6;

    -- Return the new gamer's ID as final confirmation
    SELECT @NewGamerID AS NewGamerID,
           'Onboarding complete!' AS Message;

END;
GO
-- USAGE (new gamer, no existing games):
-- DECLARE @ID INT;
-- EXEC sp_FullGamerOnboarding
--     @FirstName='Sam', @LastName='Lee',
--     @Email='sam.lee@email.com',
--     @PasswordHash=HASHBYTES('SHA2_256', N'sam_password'),
--     @PreferredGenres='Action, RPG', @PreferredDifficulty='Hard',
--     @PreferredMode='Single-Player', @AvailablePlayTime=20.0;
--
-- USAGE (gamer who already owns Diablo IV, Far Cry 6, and Battlefield 2042):
-- EXEC sp_FullGamerOnboarding
--     @FirstName='Sam', @LastName='Lee',
--     @Email='sam2@email.com',
--     @PasswordHash=HASHBYTES('SHA2_256', N'sam2_password'),
--     @PreferredGenres='Action',
--     @OwnedGameTitles='Diablo IV|Far Cry 6|Battlefield 2042';


