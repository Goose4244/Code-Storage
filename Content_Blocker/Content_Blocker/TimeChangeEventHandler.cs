using System;
using Microsoft.Win32;
using System.Threading;

public class TimeChangeEventHandler
{
    public bool timeChanged = false;
    private int correctingTime = 0;

    public void InitializeTimeChangeEventHandler()
    {
        SystemEvents.TimeChanged += OnSystemTimeChanged;
    }

    private void OnSystemTimeChanged(object? sender, EventArgs e)
    {
        // Ignore time changes caused by our own correction.
        if (Volatile.Read(ref correctingTime) == 1)
            return;

        timeChanged = true;
    }

    public void BeginTimeCorrection()
    {
        Interlocked.Exchange(ref correctingTime, 1);
        timeChanged = false;
    }

    public void EndTimeCorrection()
    {
        timeChanged = false;
        Interlocked.Exchange(ref correctingTime, 0);
    }

}