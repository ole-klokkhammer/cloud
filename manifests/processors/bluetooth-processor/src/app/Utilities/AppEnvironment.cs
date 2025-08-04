using System;

public static class AppEnvironment
{
    public static string LogLevel =>
        Environment.GetEnvironmentVariable("LOG_LEVEL") ?? throw new InvalidOperationException("LOG_LEVEL is not set.");

    public static string RabbitMqHost =>
        Environment.GetEnvironmentVariable("RABBITMQ_HOST") ?? throw new InvalidOperationException("RABBITMQ_BROKER is not set.");

    public static string RabbitMqUser =>
        Environment.GetEnvironmentVariable("RABBITMQ_USER") ?? throw new InvalidOperationException("RABBITMQ_USER is not set.");

    public static string RabbitMqPassword =>
        Environment.GetEnvironmentVariable("RABBITMQ_PASSWORD") ?? throw new InvalidOperationException("RABBITMQ_PASSWORD is not set.");

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