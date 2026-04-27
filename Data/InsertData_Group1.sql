USE mist460-api-group1;
GO

-- ============================================================
-- AppUser (8 rows: 5 Gamers, 3 Developers)
-- ============================================================

INSERT INTO AppUser (FirstName, LastName, Phone, Email, PasswordHash, UserRole)
VALUES
-- Gamers
(N'Alex',    N'Rivera',   N'304-555-0101', N'alex.rivera@email.com',      CONVERT(VARBINARY(256), 'hash_alex123'),    N'Gamer'),
(N'Jordan',  N'Kim',      N'304-555-0102', N'jordan.kim@email.com',       CONVERT(VARBINARY(256), 'hash_jordan456'),  N'Gamer'),
(N'Morgan',  N'Patel',    N'304-555-0103', N'morgan.patel@email.com',     CONVERT(VARBINARY(256), 'hash_morgan789'),  N'Gamer'),
(N'Taylor',  N'Nguyen',   N'304-555-0104', N'taylor.nguyen@email.com',    CONVERT(VARBINARY(256), 'hash_taylor321'),  N'Gamer'),
(N'Casey',   N'Johnson',  NULL,            N'casey.johnson@email.com',    CONVERT(VARBINARY(256), 'hash_casey654'),   N'Gamer'),
-- Developers (real AAA publishers)
(N'Bobby',   N'Kotick',   N'310-555-0201', N'bobby.kotick@activision.com',CONVERT(VARBINARY(256), 'hash_act111'),     N'Developer'),
(N'Andrew',  N'Wilson',   N'650-555-0202', N'andrew.wilson@ea.com',       CONVERT(VARBINARY(256), 'hash_ea222'),      N'Developer'),
(N'Yves',    N'Guillemot',N'212-555-0203', N'yves.g@ubisoft.com',         CONVERT(VARBINARY(256), 'hash_ubi333'),     N'Developer');
GO

-- ============================================================
-- Gamer (AppUserID 1-5)
-- ============================================================

INSERT INTO Gamer (GamerID, PreferredGenres, PreferredDifficulty, PreferredPlayStyle, PreferredMode, AvailablePlayTime)
VALUES
(1, N'FPS, Action',        N'Hard',    N'Completionist',  N'Multiplayer',   20.0),
(2, N'Sports, Racing',     N'Medium',  N'Casual',         N'Multiplayer',   10.0),
(3, N'RPG, Action',        N'Expert',  N'Speedrunner',    N'Single-Player', 25.0),
(4, N'Adventure, Action',  N'Medium',  N'Story-Driven',   N'Single-Player', 12.0),
(5, N'FPS, Sports',        N'Easy',    N'Casual',         N'Co-op',          8.0);
GO

-- ============================================================
-- Developer (AppUserID 6-8)
-- ============================================================

INSERT INTO Developer (DeveloperID, StudioName, StudioWebsite)
VALUES
(6, N'Activision Blizzard', N'https://www.activisionblizzard.com'),
(7, N'Electronic Arts',     N'https://www.ea.com'),
(8, N'Ubisoft',             N'https://www.ubisoft.com');
GO

-- ============================================================
-- Genre (9 rows)
-- ============================================================

INSERT INTO Genre (GenreName)
VALUES
(N'Action'),
(N'First-Person Shooter'),
(N'Sports'),
(N'RPG'),
(N'Adventure'),
(N'Racing'),
(N'Battle Royale'),
(N'Strategy'),
(N'Open World');
GO

-- ============================================================
-- Game (9 rows - real AAA titles)
-- ============================================================

INSERT INTO Game (DeveloperID, GameTitle, GameDescription, YearReleased, AverageRating)
VALUES
(6, N'Call of Duty: Modern Warfare III',  N'Tactical FPS with iconic multiplayer modes and a gripping campaign.',              2023, 3.90),
(6, N'Diablo IV',                         N'Dark action RPG set in the world of Sanctuary with deep loot and build systems.',  2023, 4.20),
(6, N'World of Warcraft: The War Within', N'Massively multiplayer online RPG set in the iconic Warcraft universe.',            2024, 4.10),
(7, N'EA Sports FC 25',                   N'The most realistic football simulation with updated rosters and gameplay.',        2024, 3.80),
(7, N'Battlefield 2042',                  N'Large-scale multiplayer FPS featuring futuristic warfare and 128-player lobbies.', 2021, 3.20),
(7, N'The Sims 4',                        N'Life simulation game where players create and control people in a virtual world.', 2014, 4.00),
(8, N'Assassin''s Creed Mirage',          N'Action-adventure game returning to the roots of stealth in 9th-century Baghdad.', 2023, 4.10),
(8, N'Far Cry 6',                         N'Open world FPS set on a fictional Caribbean island under a ruthless dictator.',    2021, 3.70),
(8, N'Rainbow Six Siege',                 N'Tactical 5v5 FPS built around destructible environments and operator abilities.', 2015, 4.40);
GO

-- ============================================================
-- GameGenre (many-to-many, ~2 genres per game)
-- ============================================================

INSERT INTO GameGenre (GameID, GenreID)
VALUES
(1, 2),   -- CoD: MW3            -> First-Person Shooter
(1, 7),   -- CoD: MW3            -> Battle Royale
(2, 1),   -- Diablo IV           -> Action
(2, 4),   -- Diablo IV           -> RPG
(3, 4),   -- WoW: The War Within -> RPG
(3, 1),   -- WoW: The War Within -> Action
(4, 3),   -- EA Sports FC 25     -> Sports
(5, 2),   -- Battlefield 2042    -> First-Person Shooter
(5, 1),   -- Battlefield 2042    -> Action
(6, 8),   -- The Sims 4          -> Strategy
(7, 5),   -- AC Mirage           -> Adventure
(7, 9),   -- AC Mirage           -> Open World
(8, 9),   -- Far Cry 6           -> Open World
(8, 2),   -- Far Cry 6           -> First-Person Shooter
(9, 2),   -- Rainbow Six Siege   -> First-Person Shooter
(9, 1);   -- Rainbow Six Siege   -> Action
GO

-- ============================================================
-- Library (9 rows - one row per Gamer + Game they own)
-- ============================================================

INSERT INTO Library (GamerID, GameID, DateAdded)
VALUES
(1, 1, '2023-11-10'),   -- Alex     owns CoD: MW3
(1, 9, '2022-03-15'),   -- Alex     owns Rainbow Six Siege
(2, 4, '2024-09-27'),   -- Jordan   owns EA Sports FC 25
(2, 1, '2023-12-01'),   -- Jordan   owns CoD: MW3
(3, 2, '2023-06-06'),   -- Morgan   owns Diablo IV
(3, 7, '2023-10-05'),   -- Morgan   owns AC Mirage
(4, 7, '2023-10-20'),   -- Taylor   owns AC Mirage
(4, 8, '2021-10-07'),   -- Taylor   owns Far Cry 6
(5, 5, '2021-11-19');   -- Casey    owns Battlefield 2042
GO

-- ============================================================
-- PlayerStats (9 rows - one per Library entry)
-- ============================================================

INSERT INTO PlayerStats (LibraryID, HoursPlayed, Status)
VALUES
(1,  210.0, N'In Progress'),   -- Alex / CoD: MW3
(2,  340.0, N'Completed'),     -- Alex / Rainbow Six Siege
(3,   55.0, N'In Progress'),   -- Jordan / EA Sports FC 25
(4,   80.0, N'Completed'),     -- Jordan / CoD: MW3
(5,  125.0, N'In Progress'),   -- Morgan / Diablo IV
(6,   40.0, N'Completed'),     -- Morgan / AC Mirage
(7,   38.0, N'In Progress'),   -- Taylor / AC Mirage
(8,   22.0, N'Abandoned'),     -- Taylor / Far Cry 6
(9,   15.0, N'In Progress');   -- Casey / Battlefield 2042
GO

-- ============================================================
-- GamerReview (9 rows - only for games the gamer owns)
-- ============================================================

INSERT INTO GamerReview (GamerID, GameID, ReviewText, Rating, ReviewDate)
VALUES
(1, 1, N'MW3 multiplayer is as addictive as ever. Campaign felt a little short though.',              3.8, '2023-12-15'),
(1, 9, N'Rainbow Six Siege has the best tactical FPS gameplay out there. Still going strong.',        4.9, '2023-01-20'),
(2, 4, N'FC 25 feels smoother than ever. Ultimate Team is still a money pit though.',                 3.7, '2024-10-10'),
(2, 1, N'Fun with friends in Warzone but the base multiplayer maps are hit or miss.',                 3.5, '2024-01-05'),
(3, 2, N'Diablo IV is absolutely massive. The endgame keeps me hooked for hundreds of hours.',        4.5, '2023-09-01'),
(3, 7, N'AC Mirage brings back the classic stealth feel. Short but very well crafted.',               4.2, '2023-11-22'),
(4, 7, N'Loved the setting and story. Wish it were a bit longer but very enjoyable.',                 4.0, '2023-12-01'),
(4, 8, N'Far Cry 6 looks gorgeous but the story does not live up to the hype.',                      3.3, '2022-02-14'),
(5, 5, N'Battlefield 2042 had a rough launch but it has improved a lot with patches.',                3.5, '2022-06-30');
GO
