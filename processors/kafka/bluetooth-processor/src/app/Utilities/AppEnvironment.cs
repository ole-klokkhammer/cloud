using System;

public static class AppEnvironment
{
    public static string KafkaBroker =>
        Environment.GetEnvironmentVariable("KAFKA_BROKER") ?? throw new InvalidOperationException("KAFKA_BROKER is not set.");

    public static string KafkaTopic =>
        Environment.GetEnvironmentVariable("KAFKA_TOPIC") ?? throw new InvalidOperationException("KAFKA_TOPIC is not set.");

    public static string DbHost =>
        Environment.GetEnvironmentVariable("DB_HOST") ?? throw new InvalidOperationException("DB_HOST is not set.");

    public static string DbPort =>
        Environment.GetEnvironmentVariable("DB_PORT") ?? "5432";

    public static string DbUser =>
        Environment.GetEnvironmentVariable("DB_USER") ?? throw new InvalidOperationException("DB_USER is not set.");

    public static string DbPassword =>
        Environment.GetEnvironmentVariable("DB_PASSWORD") ?? throw new InvalidOperationException("DB_PASSWORD is not set.");

    public static string DbName =>
        Environment.GetEnvironmentVariable("DB_NAME") ?? throw new InvalidOperationException("DB_NAME is not set.");
}