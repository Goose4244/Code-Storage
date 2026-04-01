using System;
using System.Diagnostics;
using System.Threading;

struct PlayerStats
{
    public float player_speed;
    public float player_jump;
    public int player_health;
}

struct LevelConfig
{
    public float level_speed;
    public float level_length;
    public ConsoleColor platColor;
    public ConsoleColor groundColor;
    public string level_name;
}

class Program
{
    static LevelConfig[] levels = {
        new LevelConfig { level_speed = 14f, level_length = 600f, platColor = ConsoleColor.Yellow, groundColor = ConsoleColor.Green, level_name = "Level 1" },
        new LevelConfig { level_speed = 19f, level_length = 700f, platColor = ConsoleColor.Gray, groundColor = ConsoleColor.DarkGray, level_name = "Level 2" },
        new LevelConfig { level_speed = 24f, level_length = 800f, platColor = ConsoleColor.Cyan, groundColor = ConsoleColor.DarkBlue, level_name = "Level 3" },
        new LevelConfig { level_speed = 29f, level_length = 900f, platColor = ConsoleColor.DarkRed, groundColor = ConsoleColor.White, level_name = "Level 4" },
        new LevelConfig { level_speed = 35f, level_length = 1000f, platColor = ConsoleColor.Magenta, groundColor = ConsoleColor.DarkMagenta, level_name = "Level 5" },
    };

    static PlayerStats StartMenu()
    {
        Console.Clear();
        Console.CursorVisible = false;
        Console.WriteLine("=== Start Menu ===\n");
        Console.WriteLine("Press ENTER to start...");
        Console.WriteLine("\nUse A/D or Left/Right to move, Space to jump.");

        while (true)
        {
            var key = Console.ReadKey(true).Key;
            if (key == ConsoleKey.Enter)
                break;
        }

        // Return default stats
        return new PlayerStats { player_speed = 20f, player_jump = -22f, player_health = 2 };
    }

    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        PlayerStats stats = StartMenu();
        int currentLevel = 0;

        while (currentLevel < levels.Length)
        {
            // 0 = quit, 1 = dead, 2 = win
            int result = RunGame(stats, levels[currentLevel]);

            if (result == 2)
            {
                currentLevel++;

                if (currentLevel >= levels.Length)
                {
                    Console.Clear();
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    Console.WriteLine("=== YOU WON ===\n");
                    Console.ForegroundColor = ConsoleColor.White;
                    Console.WriteLine("Congratulations on beating our game!");
                    Console.WriteLine("Thanks for playing!");
                    Console.WriteLine("\nPress any key to exit...");
                    Console.ReadKey(true);
                    break;
                }

                Console.Clear();
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("Level Complete!\n");
                Console.ForegroundColor = ConsoleColor.White;
                Console.WriteLine("Next: " + levels[currentLevel].level_name);
                Console.WriteLine("\nPress any key...");
                Console.ReadKey(true);
            }
            else if (result == 1)
            {
                if (!GameOver()) break;
                currentLevel = 0;
                stats = StartMenu();
            }
            else
            {
                break;
            }
        }
    }

    static int RunGame(PlayerStats stats, LevelConfig lvl)
    {
        int width = 80, height = 20;
        Console.SetWindowSize(width, height);
        Console.SetBufferSize(width, height);
        Console.CursorVisible = false;

        float player_x_position = 20, player_y_position = 0; 
        float vertical_velocity = 0;
        float gravity = 30f;

        // Damage cooldown
        Stopwatch hitCooldownTimer = new Stopwatch();
        hitCooldownTimer.Start();
        double lastHitTime = -2;

        float moveSpeed = stats.player_speed;
        float jumpForce = stats.player_jump;
        float scrollSpeed = lvl.level_speed;

        float airTime = (2 * -jumpForce) / gravity;
        float jumpDist = scrollSpeed * airTime;

        bool grounded = false;
        float scrolled = 0f;
        float finishX = -1f;

        int floorY = height - 4; 

        Random rand = new Random();
        int platCount = 8;
        float[,] plats = new float[platCount, 3];

        float cumulative_x = 10f;
        int prevY = floorY;
        float jumpHeight = (jumpForce * jumpForce) / (2 * gravity) * -1;

        for (int platform_index = 0; platform_index < platCount; platform_index++)
        {
            int minY = Math.Max(0, prevY - (int)Math.Abs(jumpHeight));
            int maxY = Math.Min(floorY - 1, prevY + (int)Math.Abs(jumpHeight));
            plats[platform_index, 2] = rand.Next(minY, maxY + 1);
            plats[platform_index, 1] = rand.Next(5, 12);
            plats[platform_index, 0] = cumulative_x;
            cumulative_x += jumpDist * 0.8f;
            prevY = (int)plats[platform_index, 2];
        }

        int spikeCount = 15;
        float[] spikes = new float[spikeCount];
        for (int spike_index = 0; spike_index < spikeCount; spike_index++)
            spikes[spike_index] = rand.Next(0, width);

        Stopwatch stopwatch = Stopwatch.StartNew();

        string heartChar = "♥"; 

        while (true)
        {
            double deltaTime = stopwatch.Elapsed.TotalSeconds;
            stopwatch.Restart();

            float moveInput = 0;
            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true).Key;
                if (key == ConsoleKey.A || key == ConsoleKey.LeftArrow) moveInput = -1;
                if (key == ConsoleKey.D || key == ConsoleKey.RightArrow) moveInput = 1;
                if (key == ConsoleKey.Spacebar && grounded) { vertical_velocity = jumpForce; grounded = false; }
                if (key == ConsoleKey.Escape) return 0;
            }

            // Player movement
            int step = Math.Max(1, (int)(moveSpeed / 5f));
            player_x_position += moveInput * step;
            if (player_x_position < 0) player_x_position = 0;
            if (player_x_position > width - 1) player_x_position = width - 1;


            float scroll = scrollSpeed * (float)deltaTime;
            scrolled += scroll;


            for (int i = 0; i < platCount; i++) plats[i, 0] -= scroll;
            for (int i = 0; i < spikeCount; i++)
            {
                spikes[i] -= scroll;
                if (spikes[i] < 0) spikes[i] = width + rand.Next(5, 20);
            }

            // Generate new platforms
            for (int i = 0; i < platCount; i++)
            {
                if (plats[i, 0] + plats[i, 1] < 0)
                {
                    float rightMost = 0;
                    for (int j = 0; j < platCount; j++)
                        if (plats[j, 0] > rightMost) rightMost = plats[j, 0];
                    plats[i, 0] = rightMost + jumpDist * 0.8f;
                    plats[i, 1] = rand.Next(5, 12);
                    plats[i, 2] = rand.Next(0, floorY);
                }
            }

            // Finish line
            if (scrolled >= lvl.level_length && finishX < 0) finishX = width + 5f;
            if (finishX >= 0) finishX -= scroll;

            // Physics
            vertical_velocity += gravity * (float)deltaTime;
            player_y_position += vertical_velocity * (float)deltaTime;
            grounded = false;

            // Floor collision & spike damage
            if (player_y_position >= floorY)
            {
                player_y_position = floorY;
                vertical_velocity = 0;
                grounded = true;

                for (int i = 0; i < spikeCount; i++)
                {
                    if ((int)player_x_position == (int)spikes[i])
                    {
                        double currentTime = hitCooldownTimer.Elapsed.TotalSeconds;
                        if (currentTime - lastHitTime >= 2.0)
                        {
                            stats.player_health--;
                            lastHitTime = currentTime;
                            if (stats.player_health <= 0) return 1;
                        }
                    }
                }
            }

            // Platform collisions
            for (int i = 0; i < platCount; i++)
            {
                int platX = (int)plats[i, 0];
                int platW = (int)plats[i, 1];
                int platY = (int)plats[i, 2];

                if (vertical_velocity >= 0 && player_y_position >= platY - 1 && player_y_position <= platY && player_x_position >= platX && player_x_position <= platX + platW)
                {
                    player_y_position = platY - 1;
                    vertical_velocity = 0;
                    grounded = true;
                }
            }

            if (player_y_position < 0) player_y_position = 0;
            if (player_y_position > floorY) player_y_position = floorY;

            if (finishX >= 0 && Math.Abs(player_x_position - finishX) < 1.5f) return 2;

            // --- RENDER ---
            Console.Clear();

            // Row 0: Health hearts
            Console.SetCursorPosition(0, 0);
            Console.ForegroundColor = ConsoleColor.Red;
            for (int i = 0; i < stats.player_health; i++) Console.Write(heartChar + " ");
            Console.ForegroundColor = ConsoleColor.White;

            // Row 1: Progress bar
            int barWidth = width - 2;
            float progress = scrolled / lvl.level_length;
            if (progress > 1f) progress = 1f;
            int filled = (int)(barWidth * progress);
            Console.SetCursorPosition(0, 1);
            Console.ForegroundColor = ConsoleColor.DarkGray;
            Console.Write("[" + new string('=', filled) + new string('-', barWidth - filled) + "]");

            // Player (shifted down 2 rows)
            Console.SetCursorPosition((int)player_x_position, (int)player_y_position + 2);
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.Write("■");

            // Ground
            Console.SetCursorPosition(0, height - 1);
            Console.ForegroundColor = lvl.groundColor;
            Console.Write(new string('#', width));

            // Spikes
            Console.ForegroundColor = ConsoleColor.Red;
            for (int i = 0; i < spikeCount; i++)
            {
                int sx = (int)spikes[i];
                if (sx >= 0 && sx < width)
                {
                    Console.SetCursorPosition(sx, height - 1);
                    Console.Write("^");
                }
            }

            // Platforms
            Console.ForegroundColor = lvl.platColor;
            for (int i = 0; i < platCount; i++)
            {
                int dx = (int)plats[i, 0];
                int dy = (int)plats[i, 2];
                int dw = (int)plats[i, 1];
                if (dx < width && dx + dw > 0)
                {
                    int vis = Math.Min(dw, width - Math.Max(dx, 0));
                    if (vis > 0)
                    {
                        Console.SetCursorPosition(Math.Max(dx, 0), dy + 2); // shifted down 2
                        Console.Write(new string('-', vis));
                    }
                }
            }

            // Finish line
            if (finishX >= 0 && (int)finishX >= 0 && (int)finishX < width)
            {
                Console.ForegroundColor = ConsoleColor.White;
                for (int row = 2; row < height - 1; row++)
                {
                    Console.SetCursorPosition((int)finishX, row);
                    Console.Write("‖");
                }
            }

            Thread.Sleep(16);
        }
    }



    static bool GameOver()
    {
        while (Console.KeyAvailable)
            Console.ReadKey(true); // Clear input buffer

        Console.Clear();
        Console.ForegroundColor = ConsoleColor.Red;
        Console.WriteLine("=== GAME OVER ===\n");
        Console.ForegroundColor = ConsoleColor.White;
        Console.WriteLine("Restart from level 1? (Y/N)");

        while (true)
        {
            var k = Console.ReadKey(true).Key;
            if (k == ConsoleKey.Y) return true;
            if (k == ConsoleKey.N) return false;
        }
    }
}