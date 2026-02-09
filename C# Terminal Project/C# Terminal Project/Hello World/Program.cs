using System;
using System.Diagnostics;
using System.Threading;

class Program
{
    static void Main()
    {
        // World settings
        int worldWidth = 60;
        int worldHeight = 20;

        // Make sure console is large enough
        Console.SetWindowSize(Math.Max(worldWidth, 20), Math.Max(worldHeight, 20));
        Console.SetBufferSize(Math.Max(worldWidth, 20), Math.Max(worldHeight, 20));
        Console.CursorVisible = false;

        // Player Variables
        float playerX = 20;
        float playerY = 10;
        float velocityY = 0;

        float gravity = 25f;
        float jumpForce = -20f; // Strong jump
        float moveSpeed = 25f;

        // Max jump height
        float jumpHeight = (jumpForce * jumpForce) / (2 * gravity);

        bool isGrounded = false;

        // Random platform generation
        Random rand = new Random();
        int platformCount = 8;
        int minPlatformWidth = 5;
        int maxPlatformWidth = 12;

        int[,] platforms = new int[platformCount, 3]; // [xStart, width, y]

        int floorY = worldHeight - 2;  // Floor position
        int topMargin = 3;             // Leave at least 3 lines at top
        int previousY = floorY;

        for (int i = 0; i < platformCount; i++)
        {
            // Max height for next platform (not above topMargin)
            int maxY = Math.Max(topMargin, previousY - (int)jumpHeight);
            int upper = Math.Max(maxY, previousY - 1);

            platforms[i, 2] = rand.Next(maxY, upper + 1); // Y position
            platforms[i, 1] = rand.Next(minPlatformWidth, maxPlatformWidth); // width
            platforms[i, 0] = rand.Next(0, worldWidth - platforms[i, 1]); // X start

            previousY = platforms[i, 2];
        }

        Stopwatch sw = Stopwatch.StartNew();

        while (true)
        {
            double dt = sw.Elapsed.TotalSeconds;
            sw.Restart();

            // Input
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
                if (key == ConsoleKey.Escape) return;
            }

            // Horizontal movement
            playerX += moveInput * moveSpeed * (float)dt;
            playerX = Math.Clamp(playerX, 0, worldWidth - 1);

            // Physics
            velocityY += gravity * (float)dt;
            playerY += velocityY * (float)dt;
            isGrounded = false;

            // Floor collision
            if (playerY >= worldHeight - 2)
            {
                playerY = worldHeight - 2;
                velocityY = 0;
                isGrounded = true;
            }

            // Platform collision (from above only)
            for (int i = 0; i < platformCount; i++)
            {
                int platX = platforms[i, 0];
                int platW = platforms[i, 1];
                int platY = platforms[i, 2];

                if (playerY >= platY - 1 && playerY <= platY && playerX >= platX && playerX <= platX + platW)
                {
                    playerY = platY - 1;
                    velocityY = 0;
                    isGrounded = true;
                }
            }

            // Clamp vertical position to console height
            playerY = Math.Clamp(playerY, 0, worldHeight - 2);

            // Render
            Console.Clear();

            // Draw player
            Console.SetCursorPosition((int)playerX, (int)playerY);
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.Write("■");

            // Draw floor
            Console.SetCursorPosition(0, worldHeight - 1);
            Console.ForegroundColor = ConsoleColor.Green;
            Console.Write(new string('#', worldWidth));

            // Draw platforms
            Console.ForegroundColor = ConsoleColor.Yellow;
            for (int i = 0; i < platformCount; i++)
            {
                Console.SetCursorPosition(platforms[i, 0], platforms[i, 2]);
                Console.Write(new string('-', platforms[i, 1]));
            }

            Thread.Sleep(16);
        }
    }
}
