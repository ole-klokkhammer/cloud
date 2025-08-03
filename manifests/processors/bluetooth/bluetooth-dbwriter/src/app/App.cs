
using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

public class App
{
    public async Task RunAsync(string[] args)
    {
        var cts = new CancellationTokenSource();
        Console.CancelKeyPress += (_, e) => { e.Cancel = true; cts.Cancel(); };
        AppDomain.CurrentDomain.ProcessExit += (_, __) => cts.Cancel();

        var services = new ServiceCollection();
        services.AddLogging(builder =>
        {
            builder.AddSimpleConsole(options =>
            {
                options.TimestampFormat = "[yyyy-MM-dd HH:mm:ss] ";
                options.IncludeScopes = false;
            });
            builder.SetMinimumLevel(LogLevel.Information);
        });
        services.AddSingleton<JsonUtil>();
        services.AddSingleton<MqttService>();
        services.AddSingleton<AirthingsService>();
        services.AddSingleton<PostgresService>();
        services.AddSingleton<AirthingsRepository>();
        services.AddSingleton<BluetoothRepository>();
        services.AddSingleton<HomeassistantService>();
        services.AddSingleton<RabbitMqConnectionService>();
        services.AddSingleton<BluetoothScanConsumer>();


        using var provider = services.BuildServiceProvider();
        var postgresService = provider.GetRequiredService<PostgresService>();
        var mqttService = provider.GetRequiredService<MqttService>();
        var rabbitmqService = provider.GetRequiredService<RabbitMqConnectionService>();
        var bluetoothScanConsumer = provider.GetRequiredService<BluetoothScanConsumer>();

        try
        {
            postgresService.Initialize();
            await mqttService.InitializeAsync();
            await rabbitmqService.InitializeAsync();

            await Task.WhenAll(
                bluetoothScanConsumer.Consume(cts.Token)
            );
        }
        finally
        {
            // Ensure graceful shutdown 
            rabbitmqService.Dispose();
            await mqttService.Shutdown();
            await postgresService.Shutdown();
        }
    }
}