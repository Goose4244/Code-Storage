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
                currentLevel ++;

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

        Stopwatch hitCooldownTimer = new Stopwatch();
        hitCooldownTimer.Start();
        double lastHitTime = -2;

        float moveSpeed = stats.player_speed;
        float jumpForce = stats.player_jump;
        float scrollSpeed = lvl.level_speed;

        bool grounded = false;
        float scrolled = 0f;
        float finishX = -1f;

        int floorY = height - 4;

        Random rand = new Random();
        int platCount = 8;
        float[,] plats = new float[platCount, 3]; // x, width, y

        // Place starting platforms spread across the screen
        for (int platform_index = 0; platform_index < platCount; platform_index++)
        {
            plats[platform_index, 0] = 10 + platform_index * 20;
            plats[platform_index, 1] = rand.Next(5, 12);
            plats[platform_index, 2] = rand.Next(3, floorY - 1);
        }

        int spikeCount = 25;
        float[] spikes = new float[spikeCount];
        for (int spike_index = 0; spike_index < spikeCount; spike_index++)
            spikes[spike_index] = rand.Next(0, width);

        Stopwatch stopwatch = Stopwatch.StartNew();
        string heartChar = "♥";

        while (true)
        {
            double deltaTime = stopwatch.Elapsed.TotalSeconds;
            stopwatch.Restart();

            if (deltaTime > 0.1) deltaTime = 0.1;

            float moveInput = 0;
            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true).Key;
                if (key == ConsoleKey.A || key == ConsoleKey.LeftArrow) moveInput = -1;
                if (key == ConsoleKey.D || key == ConsoleKey.RightArrow) moveInput = 1;
                if (key == ConsoleKey.Spacebar && grounded) { vertical_velocity = jumpForce; grounded = false; }
                if (key == ConsoleKey.Escape) return 0;
            }

            int step = Math.Max(1, (int)(moveSpeed / 5f));
            player_x_position += moveInput * step;
            if (player_x_position < 0) player_x_position = 0;
            if (player_x_position > width - 1) player_x_position = width - 1;

            float scroll = scrollSpeed * (float)deltaTime;
            scrolled += scroll;

            // Scroll platforms and spikes
            for (int plat_move_index = 0; plat_move_index < platCount; plat_move_index++)
                plats[plat_move_index, 0] -= scroll;

            for (int spike_move_index = 0; spike_move_index < spikeCount; spike_move_index++)
            {
                spikes[spike_move_index] -= scroll;
                if (spikes[spike_move_index] < 0)
                    spikes[spike_move_index] = width + rand.Next(5, 20);
            }

            // Recycle platforms
            for (int plat_recycle_index = 0; plat_recycle_index < platCount; plat_recycle_index++)
            {
                if (plats[plat_recycle_index, 0] + plats[plat_recycle_index, 1] < 0)
                {
                    float rightMost = 0;
                    for (int plat_scan_index = 0; plat_scan_index < platCount; plat_scan_index++)
                        if (plats[plat_scan_index, 0] > rightMost) rightMost = plats[plat_scan_index, 0];

                    plats[plat_recycle_index, 0] = rightMost + rand.Next(15, 30);
                    plats[plat_recycle_index, 1] = rand.Next(5, 12);
                    plats[plat_recycle_index, 2] = rand.Next(3, floorY - 1);
                }
            }

            // Spawn finish line once enough distance is scrolled
            if (scrolled >= lvl.level_length && finishX < 0)
                finishX = width + 5f;
            if (finishX >= 0)
                finishX -= scroll;

            // Y Physics
            vertical_velocity += gravity * (float)deltaTime;
            player_y_position += vertical_velocity * (float)deltaTime;
            grounded = false;

            // Floor collision
            if (player_y_position >= floorY)
            {
                player_y_position = floorY;
                vertical_velocity = 0;
                grounded = true;

                for (int spike_collision_index = 0; spike_collision_index < spikeCount; spike_collision_index++)
                {
                    if ((int)player_x_position == (int)spikes[spike_collision_index])
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

            // Platform collision
            for (int plat_collision_index = 0; plat_collision_index < platCount; plat_collision_index++)
            {
                int plat_x = (int)plats[plat_collision_index, 0];
                int plat_width = (int)plats[plat_collision_index, 1];
                int plat_y = (int)plats[plat_collision_index, 2];

                bool above_platform = player_y_position >= plat_y - 1 && player_y_position <= plat_y;
                bool within_platform_x = player_x_position >= plat_x && player_x_position <= plat_x + plat_width;

                if (vertical_velocity >= 0 && above_platform && within_platform_x)
                {
                    player_y_position = plat_y - 1;
                    vertical_velocity = 0;
                    grounded = true;
                }
            }

            if (player_y_position < 0) player_y_position = 0;
            if (player_y_position > floorY) player_y_position = floorY;

            if (finishX >= 0 && Math.Abs(player_x_position - finishX) < 1.5f) return 2;

            // Render
            Console.Clear();

            Console.SetCursorPosition(0, 0);
            Console.ForegroundColor = ConsoleColor.Red;
            for (int health_heart_index = 0; health_heart_index < stats.player_health; health_heart_index++)
                Console.Write(heartChar + " ");

            int barWidth = width - 2;
            float progress = scrolled / lvl.level_length;
            if (progress > 1f) progress = 1f;
            int filled = (int)(barWidth * progress);
            Console.SetCursorPosition(0, 1);
            Console.ForegroundColor = ConsoleColor.DarkGray;
            Console.Write("[" + new string('=', filled) + new string('-', barWidth - filled) + "]");

            Console.SetCursorPosition((int)player_x_position, (int)player_y_position + 2);
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.Write("■");

            Console.SetCursorPosition(0, height - 1);
            Console.ForegroundColor = lvl.groundColor;
            Console.Write(new string('#', width));

            Console.ForegroundColor = ConsoleColor.Red;
            for (int spike_draw_index = 0; spike_draw_index < spikeCount; spike_draw_index++)
            {
                int spike_x = (int)spikes[spike_draw_index];
                if (spike_x >= 0 && spike_x < width)
                {
                    Console.SetCursorPosition(spike_x, height - 1);
                    Console.Write("^");
                }
            }

            Console.ForegroundColor = lvl.platColor;
            for (int plat_draw_index = 0; plat_draw_index < platCount; plat_draw_index++)
            {
                int current_plat_x = (int)plats[plat_draw_index, 0];
                int current_plat_y = (int)plats[plat_draw_index, 2];
                int current_plat_width = (int)plats[plat_draw_index, 1];

                if (current_plat_x < width && current_plat_x + current_plat_width > 0)
                {
                    int visible = Math.Min(current_plat_width, width - Math.Max(current_plat_x, 0));
                    if (visible > 0)
                    {
                        Console.SetCursorPosition(Math.Max(current_plat_x, 0), current_plat_y + 2);
                        Console.Write(new string('-', visible));
                    }
                }
            }

            if (finishX >= 0 && (int)finishX >= 0 && (int)finishX < width)
            {
                Console.ForegroundColor = ConsoleColor.White;
                for (int finish_line_row = 2; finish_line_row < height - 1; finish_line_row++)
                {
                    Console.SetCursorPosition((int)finishX, finish_line_row);
                    Console.Write("‖");
                }
            }

            Thread.Sleep(16);
        }
    }

    static bool GameOver()
    {
        while (Console.KeyAvailable)
            Console.ReadKey(true);

        Console.Clear();
        Console.ForegroundColor = ConsoleColor.Red;
        Console.WriteLine("=== GAME OVER ===\n");
        Console.ForegroundColor = ConsoleColor.White;
        Console.WriteLine("Restart from level 1? (Y/N)");

        while (true)
        {
            var key = Console.ReadKey(true).Key;
            if (key == ConsoleKey.Y) return true;
            if (key == ConsoleKey.N) return false;
        }
    }
}