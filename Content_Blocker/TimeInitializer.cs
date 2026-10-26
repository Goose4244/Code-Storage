using System;
using System.Diagnostics;



public class TimeKeeper
{
    public DateTime baselineUtcTime { get; private set; }
    private Stopwatch timeElapsedStopwatch;

    public DateTime currentUtcTime { get; private set; }
    private TimeSpan elapsedStopwatchTime;

    private TimeSpan actualUtcTimeDifference;



    public void getBaselineUtcTime()
    {
        baselineUtcTime = DateTime.UtcNow;

        timeElapsedStopwatch = Stopwatch.StartNew();
    }

    public void getCurrentTimes()
    {
        currentUtcTime = DateTime.UtcNow;
        elapsedStopwatchTime = timeElapsedStopwatch.Elapsed;
    }

    public (double, DateTime) calculateTimeDifferences()
    {
        actualUtcTimeDifference = currentUtcTime - baselineUtcTime;

        DateTime expectedUtcTimeDIfference = baselineUtcTime + elapsedStopwatchTime;

        double elapsedUtcSeconds = actualUtcTimeDifference.TotalSeconds;

        double elapsedStopwatchTimeSeconds = elapsedStopwatchTime.TotalSeconds;

        double actualSecondsTimeDifference = Math.Abs(elapsedStopwatchTimeSeconds - elapsedUtcSeconds);

        return (actualSecondsTimeDifference, expectedUtcTimeDIfference);
    }

}
