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
    public static string RabbitMqExchange =>
        Environment.GetEnvironmentVariable("RABBITMQ_EXCHANGE") ?? throw new InvalidOperationException("RABBITMQ_EXCHANGE is not set.");
    public static string RabbitMqInbox =>
        Environment.GetEnvironmentVariable("RABBITMQ_INBOX") ?? throw new InvalidOperationException("RABBITMQ_INBOX is not set.");
    public static string HttpEndpoint =>
        Environment.GetEnvironmentVariable("HTTP_API_ENDPOINT") ?? throw new InvalidOperationException("HTTP_API_ENDPOINT is not set.");
}