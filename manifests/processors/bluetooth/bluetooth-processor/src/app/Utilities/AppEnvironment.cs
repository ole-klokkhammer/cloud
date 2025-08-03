using System;

public static class AppEnvironment
{
    public static string RabbitMqHost =>
        Environment.GetEnvironmentVariable("RABBITMQ_HOST") ?? throw new InvalidOperationException("RABBITMQ_BROKER is not set.");

    public static string RabbitMqUser =>
        Environment.GetEnvironmentVariable("RABBITMQ_USER") ?? throw new InvalidOperationException("RABBITMQ_USER is not set.");

    public static string RabbitMqPassword =>
        Environment.GetEnvironmentVariable("RABBITMQ_PASSWORD") ?? throw new InvalidOperationException("RABBITMQ_PASSWORD is not set.");


}