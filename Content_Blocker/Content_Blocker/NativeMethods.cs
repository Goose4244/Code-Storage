using System.Runtime.InteropServices;

public struct SystemTime
{
    public ushort Year;
    public ushort Month;
    public ushort DayOfWeek;
    public ushort Day;
    public ushort Hour;
    public ushort Minute;
    public ushort Second;
    public ushort Milliseconds;
}
public static class NativeMethods
{
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool SetSystemTime(ref SystemTime time);
}