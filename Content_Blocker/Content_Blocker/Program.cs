using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;

TimeKeeper timekeeper = new TimeKeeper();
TimeChangeEventHandler timeChangeEventHandler = new TimeChangeEventHandler();
timeChangeEventHandler.InitializeTimeChangeEventHandler();

timekeeper.getBaselineTime();

while (true)
{

    Thread.Sleep(5000);

    try
    {
        timekeeper.getCurrentTimes();
        (double actualTimeDifferenceSeconds, DateTime expectedUtcTimeDifference) = timekeeper.calculateTimeDifferences();
        Console.WriteLine($"Actual Time Difference In Seconds: {actualTimeDifferenceSeconds}");

        if (actualTimeDifferenceSeconds > 240 || timeChangeEventHandler.timeChanged == true)
        {

            Console.WriteLine($"Time difference: {actualTimeDifferenceSeconds:F2} seconds; " + $"time-change event: {timeChangeEventHandler.timeChanged}");

            SystemTime resetSystemTime = new SystemTime
            {
                Year = (ushort)expectedUtcTimeDifference.Year,
                Month = (ushort)expectedUtcTimeDifference.Month,
                Day = (ushort)expectedUtcTimeDifference.Day,
                Hour = (ushort)expectedUtcTimeDifference.Hour,
                Minute = (ushort)expectedUtcTimeDifference.Minute,
                Second = (ushort)expectedUtcTimeDifference.Second,
                Milliseconds = (ushort)expectedUtcTimeDifference.Millisecond
            };

            // Attempt to set the system time
            Console.WriteLine("TAMPERING DETECTED! Resetting system time to expected UTC time due to a significant time difference.");
            timeChangeEventHandler.BeginTimeCorrection();
            bool success = NativeMethods.SetSystemTime(ref resetSystemTime);
            timeChangeEventHandler.EndTimeCorrection();


            if (!success)
            {
                Console.WriteLine($"SetSystemTime failed. Error code: {Marshal.GetLastWin32Error()}");
            }
            else
            {
                Console.WriteLine("System time has been reset to the expected UTC time.");
            }
        }
        
        

    }

    catch (Exception ex)
    {
        Console.WriteLine($"Check failed: {ex.Message}");
    }

    finally
    {
        timekeeper.resetBaselineTime();
    }

}

