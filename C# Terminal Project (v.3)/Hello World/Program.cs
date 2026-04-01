using System;
using System.Diagnostics;
using System.Threading;

struct PlayerStats
{
    public float MoveSpeed;
    public float JumpForce;
}
// NEED TO MAKE LEVELS PLAYABLE!!!!!
class Program
{
    static PlayerStats StartMenu()
    {
        float moveSpeed = 0f;  // start at 0
        float jumpForce = 0f;  // start at 0
        int selection = 0;

        while (true)
        {
            Console.Clear();
            Console.CursorVisible = false;

            Console.WriteLine("=== PLATFORMER SETUP ===\n");
            Console.WriteLine("Use UP/DOWN to select stat");
            Console.WriteLine("Use LEFT/RIGHT to adjust");
            Console.WriteLine("Press ENTER to start\n");

            Console.WriteLine(selection == 0 ? "> Move Speed: " + moveSpeed : "  Move Speed: " + moveSpeed);
            Console.WriteLine(selection == 1 ? "> Jump Strength: " + (-jumpForce) : "  Jump Strength: " + (-jumpForce));

            var key = Console.ReadKey(true).Key;

            if (key == ConsoleKey.UpArrow) selection = Math.Max(0, selection - 1);
            if (key == ConsoleKey.DownArrow) selection = Math.Min(1, selection + 1);

            if (key == ConsoleKey.LeftArrow)
            {
                if (selection == 0) moveSpeed = Math.Max(0f, moveSpeed - 5f);  // can't go below 0
                if (selection == 1) jumpForce = Math.Min(0f, jumpForce + 2f); // can't go above 0
            }

            if (key == ConsoleKey.RightArrow)
            {
                if (selection == 0) moveSpeed = Math.Min(30f, moveSpeed + 5f);  // max 30
                if (selection == 1) jumpForce = Math.Max(-24f, jumpForce - 2f); // max jump -24
            }

            if (key == ConsoleKey.Enter)
            {
                return new PlayerStats
                {
                    MoveSpeed = moveSpeed,
                    JumpForce = jumpForce
                };
            }
        }
    }

    static void Main()
    {
        while (true)
        {
            if (!RunGame())
                break;
        }
    }

    static bool RunGame()
    {
        int worldWidth = 80;
        int worldHeight = 20;

        Console.SetWindowSize(Math.Max(worldWidth, 20), Math.Max(worldHeight, 20));
        Console.SetBufferSize(Math.Max(worldWidth, 20), Math.Max(worldHeight, 20));
        Console.CursorVisible = false;

        float playerX = 20;
        float playerY = 10;
        float velocityY = 0;

        float gravity = 30f;
        PlayerStats stats = StartMenu();

        float moveSpeed = stats.MoveSpeed;
        float jumpForce = stats.JumpForce;
        float scrollSpeed = 15f;

        float jumpHeight = (jumpForce * jumpForce) / (2 * gravity);
        float airTime = (2 * -jumpForce) / gravity;
        float jumpDistance = scrollSpeed * airTime;

        bool isGrounded = false;

        Random rand = new Random();
        int platformCount = 8;
        int minPlatformWidth = 5;
        int maxPlatformWidth = 12;

        float[,] platforms = new float[platformCount, 3];

        int floorY = worldHeight - 2;
        int topMargin = 3;
        int previousY = floorY;

        // -----------------------------
        // INITIAL PLATFORMS
        // -----------------------------
        float currentX = 0;
        for (int i = 0; i < platformCount; i++)
        {
            int maxY = Math.Max(topMargin, previousY - (int)jumpHeight);
            int upper = Math.Max(maxY, previousY - 1);

            platforms[i, 2] = rand.Next(maxY, upper + 1);
            platforms[i, 1] = rand.Next(minPlatformWidth, maxPlatformWidth);
            platforms[i, 0] = currentX;

            currentX += jumpDistance * 0.8f;
            previousY = (int)platforms[i, 2];
        }

        // -----------------------------
        // SCROLLING SPIKES
        // -----------------------------
        int spikeCount = 15;
        float[] spikes = new float[spikeCount];

        for (int i = 0; i < spikeCount; i++)
            spikes[i] = rand.Next(0, worldWidth);

        Stopwatch sw = Stopwatch.StartNew();

        while (true)
        {
            double dt = sw.Elapsed.TotalSeconds;
            sw.Restart();

            // INPUT
            float moveInput = 0;
            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true).Key;

                if (key == ConsoleKey.A || key == ConsoleKey.LeftArrow) moveInput = -1;
                if (key == ConsoleKey.D || key == ConsoleKey.RightArrow) moveInput = 1;

                if (key == ConsoleKey.Spacebar && isGrounded)
                {
                    velocityY = jumpForce;
                    isGrounded = false;
                }

                if (key == ConsoleKey.Escape)
                    return false;
            }

            // PLAYER HORIZONTAL (unchanged)
            // scaled step like before
            int movementLevel = (int)(moveSpeed / 5f);    // old 5-unit tiers
            int stepSize = Math.Max(1, movementLevel);    // at least 1 unit per frame

            playerX += moveInput * stepSize;
            playerX = Math.Clamp(playerX, 0, worldWidth - 1);

            // SCROLL PLATFORMS (unchanged)
            for (int i = 0; i < platformCount; i++)
                platforms[i, 0] -= scrollSpeed * (float)dt;

            // RECYCLE PLATFORMS (unchanged)
            for (int i = 0; i < platformCount; i++)
            {
                if (platforms[i, 0] + platforms[i, 1] < 0)
                {
                    float rightMost = 0;
                    for (int j = 0; j < platformCount; j++)
                        if (platforms[j, 0] > rightMost)
                            rightMost = platforms[j, 0];

                    float spacing = jumpDistance * 0.8f;

                    platforms[i, 0] = rightMost + spacing;
                    platforms[i, 1] = rand.Next(minPlatformWidth, maxPlatformWidth);
                    platforms[i, 2] = rand.Next(topMargin, floorY);
                }
            }

            // -----------------------------
            // SCROLL SPIKES
            // -----------------------------
            for (int i = 0; i < spikeCount; i++)
            {
                spikes[i] -= scrollSpeed * (float)dt;

                if (spikes[i] < 0)
                    spikes[i] = worldWidth + rand.Next(5, 20);
            }

            // PHYSICS (unchanged)
            velocityY += gravity * (float)dt;
            playerY += velocityY * (float)dt;
            isGrounded = false;

            // FLOOR COLLISION
            if (playerY >= floorY)
            {
                playerY = floorY;
                velocityY = 0;
                isGrounded = true;

                // SPIKE COLLISION
                for (int i = 0; i < spikeCount; i++)
                {
                    if ((int)playerX == (int)spikes[i])
                        return GameOver();
                }
            }

            // PLATFORM COLLISION (unchanged)
            for (int i = 0; i < platformCount; i++)
            {
                int platX = (int)platforms[i, 0];
                int platW = (int)platforms[i, 1];
                int platY = (int)platforms[i, 2];

                if (velocityY >= 0 &&
                    playerY >= platY - 1 &&
                    playerY <= platY &&
                    playerX >= platX &&
                    playerX <= platX + platW)
                {
                    playerY = platY - 1;
                    velocityY = 0;
                    isGrounded = true;
                }
            }

            playerY = Math.Clamp(playerY, 0, floorY);

            // RENDER (flicker preserved intentionally)
            Console.Clear();

            // Player
            Console.SetCursorPosition((int)playerX, (int)playerY);
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.Write("■");

            // Floor
            Console.SetCursorPosition(0, worldHeight - 1);
            Console.ForegroundColor = ConsoleColor.Green;
            Console.Write(new string('#', worldWidth));

            // Spikes
            Console.ForegroundColor = ConsoleColor.Red;
            for (int i = 0; i < spikeCount; i++)
            {
                int spikeX = (int)spikes[i];
                if (spikeX >= 0 && spikeX < worldWidth)
                {
                    Console.SetCursorPosition(spikeX, worldHeight - 1);
                    Console.Write("^");
                }
            }

            // Platforms
            Console.ForegroundColor = ConsoleColor.Yellow;
            for (int i = 0; i < platformCount; i++)
            {
                int drawX = (int)platforms[i, 0];
                int drawY = (int)platforms[i, 2];
                int width = (int)platforms[i, 1];

                if (drawX < worldWidth && drawX + width > 0)
                {
                    int visibleWidth = Math.Min(width, worldWidth - Math.Max(drawX, 0));
                    if (visibleWidth > 0)
                    {
                        Console.SetCursorPosition(Math.Max(drawX, 0), drawY);
                        Console.Write(new string('-', visibleWidth));
                    }
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
        Console.WriteLine("Restart? (Y/N)");

        while (true)
        {
            var key = Console.ReadKey(true).Key;

            if (key == ConsoleKey.Y)
                return true;

            if (key == ConsoleKey.N)
                return false;
        }
    }
}