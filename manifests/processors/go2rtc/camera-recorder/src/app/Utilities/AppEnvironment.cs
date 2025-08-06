using System;

public static class AppEnvironment
{
    public static string LogLevel =>
        Environment.GetEnvironmentVariable("LOG_LEVEL") ?? throw new InvalidOperationException("LOG_LEVEL is not set.");

    public static string RtspUrl =>
        Environment.GetEnvironmentVariable("RTSP_URL") ?? throw new InvalidOperationException("RTSP_URL is not set.");


    public static string OutputDirectory =>
        Environment.GetEnvironmentVariable("OUTPUT_DIRECTORY") ?? throw new InvalidOperationException("OUTPUT_DIRECTORY is not set.");
}