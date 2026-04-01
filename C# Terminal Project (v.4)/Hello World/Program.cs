using System;
using System.Diagnostics;
using System.Threading;

struct PlayerStats
{
    public float speed;
    public float jump;
}

struct LevelConfig
{
    public float spd;
    public float len;
    public ConsoleColor platColor;
    public ConsoleColor groundColor;
    public string name;
}

class Program
{
    static LevelConfig[] levels = {
        new LevelConfig { spd = 14f, len = 600f, platColor = ConsoleColor.Yellow, groundColor = ConsoleColor.Green, name = "Level 1" },
        new LevelConfig { spd = 19f, len = 700f, platColor = ConsoleColor.Gray, groundColor = ConsoleColor.DarkGray, name = "Level 2" },
        new LevelConfig { spd = 24f, len = 800f, platColor = ConsoleColor.Cyan, groundColor = ConsoleColor.DarkBlue, name = "Level 3" },
        new LevelConfig { spd = 29f, len = 900f, platColor = ConsoleColor.DarkRed, groundColor = ConsoleColor.White, name = "Level 4" },
        new LevelConfig { spd = 35f, len = 1000f, platColor = ConsoleColor.Magenta, groundColor = ConsoleColor.DarkMagenta, name = "Level 5" },
    };

    static PlayerStats StartMenu()
    {
        float spd = 0f;
        float jmp = 0f;
        int sel = 0;

        while (true)
        {
            Console.Clear();
            Console.CursorVisible = false;
            Console.WriteLine("=== PLATFORMER SETUP ===\n");
            Console.WriteLine("UP/DOWN to select, LEFT/RIGHT to adjust, ENTER to start\n");

            Console.WriteLine(sel == 0 ? "> Move Speed: " + spd : "  Move Speed: " + spd);
            Console.WriteLine(sel == 1 ? "> Jump Strength: " + (-jmp) : "  Jump Strength: " + (-jmp));

            var key = Console.ReadKey(true).Key;

            if (key == ConsoleKey.UpArrow) sel = Math.Max(0, sel - 1);
            if (key == ConsoleKey.DownArrow) sel = Math.Min(1, sel + 1);

            if (key == ConsoleKey.LeftArrow)
            {
                if (sel == 0) spd = Math.Max(0f, spd - 5f);
                if (sel == 1) jmp = Math.Min(0f, jmp + 2f);
            }
            if (key == ConsoleKey.RightArrow)
            {
                if (sel == 0) spd = Math.Min(30f, spd + 5f);
                if (sel == 1) jmp = Math.Max(-24f, jmp - 2f);
            }

            if (key == ConsoleKey.Enter)
                return new PlayerStats { speed = spd, jump = jmp };
        }
    }

    static void Main()
    {
        PlayerStats stats = StartMenu();
        int currentLevel = 0;

        while (currentLevel < levels.Length)
        {
            int result = RunGame(stats, levels[currentLevel]);

            if (result == 2)
            {
                currentLevel++;

                if (currentLevel >= levels.Length)
                {
                    Console.Clear();
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    Console.WriteLine("=== YOU WIN ===\n");
                    Console.ForegroundColor = ConsoleColor.White;
                    Console.WriteLine("You made it through all 5 areas!");
                    Console.WriteLine("\nPress any key to exit...");
                    Console.ReadKey(true);
                    break;
                }

                Console.Clear();
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("Level Complete!\n");
                Console.ForegroundColor = ConsoleColor.White;
                Console.WriteLine("Next: " + levels[currentLevel].name);
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

    // 0 = quit, 1 = dead, 2 = win
    static int RunGame(PlayerStats stats, LevelConfig lvl)
    {
        int W = 80, H = 20;
        Console.SetWindowSize(W, H);
        Console.SetBufferSize(W, H);
        Console.CursorVisible = false;

        float px = 20, py = 10;
        float vy = 0;
        float gravity = 30f;

        float moveSpeed = stats.speed;
        float jumpForce = stats.jump;
        float scrollSpeed = lvl.spd;

        float airTime = (2 * -jumpForce) / gravity;
        float jumpDist = scrollSpeed * airTime;

        bool grounded = false;
        float scrolled = 0f;
        float finishX = -1f;

        int floorY = H - 2;

        Random rand = new Random();
        int platCount = 8;
        float[,] plats = new float[platCount, 3];

        float cx = 10f;
        int prevY = floorY;
        float jumpHeight = (jumpForce * jumpForce) / (2 * gravity) * -1;

        for (int i = 0; i < platCount; i++)
        {
            int lo = Math.Max(3, prevY - (int)Math.Abs(jumpHeight));
            int hi = Math.Max(lo, prevY - 1);
            plats[i, 2] = rand.Next(lo, hi + 1);
            plats[i, 1] = rand.Next(5, 12);
            plats[i, 0] = cx;
            cx += jumpDist * 0.8f;
            prevY = (int)plats[i, 2];
        }

        int spikeCount = 15;
        float[] spikes = new float[spikeCount];
        for (int i = 0; i < spikeCount; i++)
            spikes[i] = rand.Next(0, W);

        Stopwatch sw = Stopwatch.StartNew();

        while (true)
        {
            double dt = sw.Elapsed.TotalSeconds;
            sw.Restart();

            float moveInput = 0;
            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true).Key;
                if (key == ConsoleKey.A || key == ConsoleKey.LeftArrow) moveInput = -1;
                if (key == ConsoleKey.D || key == ConsoleKey.RightArrow) moveInput = 1;
                if (key == ConsoleKey.Spacebar && grounded) { vy = jumpForce; grounded = false; }
                if (key == ConsoleKey.Escape) return 0;
            }

            int step = Math.Max(1, (int)(moveSpeed / 5f));
            px += moveInput * step;
            if (px < 0) px = 0;
            if (px > W - 1) px = W - 1;

            float scroll = scrollSpeed * (float)dt;
            scrolled += scroll;

            for (int i = 0; i < platCount; i++)
                plats[i, 0] -= scroll;

            for (int i = 0; i < platCount; i++)
            {
                if (plats[i, 0] + plats[i, 1] < 0)
                {
                    float rightMost = 0;
                    for (int j = 0; j < platCount; j++)
                        if (plats[j, 0] > rightMost) rightMost = plats[j, 0];

                    plats[i, 0] = rightMost + jumpDist * 0.8f;
                    plats[i, 1] = rand.Next(5, 12);
                    plats[i, 2] = rand.Next(3, floorY);
                }
            }

            for (int i = 0; i < spikeCount; i++)
            {
                spikes[i] -= scroll;
                if (spikes[i] < 0) spikes[i] = W + rand.Next(5, 20);
            }

            // finish line
            if (scrolled >= lvl.len && finishX < 0)
                finishX = W + 5f;
            if (finishX >= 0)
                finishX -= scroll;

            vy += gravity * (float)dt;
            py += vy * (float)dt;
            grounded = false;

            if (py >= floorY)
            {
                py = floorY;
                vy = 0;
                grounded = true;

                for (int i = 0; i < spikeCount; i++)
                    if ((int)px == (int)spikes[i]) return GameOver() ? 1 : 0;
            }

            for (int i = 0; i < platCount; i++)
            {
                int platX = (int)plats[i, 0];
                int platW = (int)plats[i, 1];
                int platY = (int)plats[i, 2];

                if (vy >= 0 && py >= platY - 1 && py <= platY && px >= platX && px <= platX + platW)
                {
                    py = platY - 1;
                    vy = 0;
                    grounded = true;
                }
            }

            if (py < 0) py = 0;
            if (py > floorY) py = floorY;

            if (finishX >= 0 && Math.Abs(px - finishX) < 1.5f)
                return 2;

            Console.Clear();

            Console.SetCursorPosition(W - lvl.name.Length - 1, 0);
            Console.ForegroundColor = ConsoleColor.White;
            Console.Write(lvl.name);

            if (finishX < 0)
            {
                int barWidth = W - 2;
                float progress = scrolled / lvl.len;
                if (progress > 1f) progress = 1f;
                int filled = (int)(barWidth * progress);
                Console.SetCursorPosition(0, 0);
                Console.ForegroundColor = ConsoleColor.DarkGray;
                Console.Write("[" + new string('=', filled) + new string('-', barWidth - filled) + "]");
            }

            Console.SetCursorPosition((int)px, (int)py);
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.Write("■");

            Console.SetCursorPosition(0, H - 1);
            Console.ForegroundColor = lvl.groundColor;
            Console.Write(new string('#', W));

            Console.ForegroundColor = ConsoleColor.Red;
            for (int i = 0; i < spikeCount; i++)
            {
                int sx = (int)spikes[i];
                if (sx >= 0 && sx < W)
                {
                    Console.SetCursorPosition(sx, H - 1);
                    Console.Write("^");
                }
            }

            Console.ForegroundColor = lvl.platColor;
            for (int i = 0; i < platCount; i++)
            {
                int dx = (int)plats[i, 0];
                int dy = (int)plats[i, 2];
                int dw = (int)plats[i, 1];

                if (dx < W && dx + dw > 0)
                {
                    int vis = Math.Min(dw, W - Math.Max(dx, 0));
                    if (vis > 0)
                    {
                        Console.SetCursorPosition(Math.Max(dx, 0), dy);
                        Console.Write(new string('-', vis));
                    }
                }
            }

            if (finishX >= 0 && (int)finishX >= 0 && (int)finishX < W)
            {
                Console.ForegroundColor = ConsoleColor.White;
                for (int row = 0; row < H - 1; row++)
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