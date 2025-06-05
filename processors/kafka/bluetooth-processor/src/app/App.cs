
using System.Text.Json;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

public class App
{
    public async Task RunAsync(string[] args)
    {
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
        services.AddSingleton<BluetoothWorker>();
        services.AddSingleton<MqttService>();
        services.AddSingleton<AirthingsService>();
        services.AddSingleton<BluetoothService>();
        services.AddSingleton<PostgresService>();
        services.AddSingleton<AirthingsRepository>();
        services.AddSingleton<BluetoothRepository>();
        services.AddSingleton<HomeassistantService>();

        using var provider = services.BuildServiceProvider();
        var bluetoothWorker = provider.GetRequiredService<BluetoothWorker>();
        var postgresService = provider.GetRequiredService<PostgresService>();
        var mqttService = provider.GetRequiredService<MqttService>();

        var cts = new CancellationTokenSource();
        Console.CancelKeyPress += (_, e) => { e.Cancel = true; cts.Cancel(); };
        AppDomain.CurrentDomain.ProcessExit += (_, __) => cts.Cancel();

        try
        {
            postgresService.Initialize();
            await mqttService.Initialize();

            await Task.WhenAll(
                bluetoothWorker.DoWork(cts.Token)
            );
        }
        finally
        {
            // Ensure graceful shutdown 
            await mqttService.Shutdown();
            await postgresService.Shutdown();
        }
    }
}