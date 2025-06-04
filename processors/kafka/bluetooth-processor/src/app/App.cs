
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

public class App
{
    public async Task RunAsync(string[] args)
    {
        var services = new ServiceCollection();

        services.AddLogging(builder =>
        {
            builder.AddConsole();
            builder.SetMinimumLevel(LogLevel.Information);
        });

        services.AddSingleton<BluetoothWorker>();
        services.AddSingleton<AirthingsService>();
        services.AddSingleton<BluetoothService>();
        services.AddSingleton<PostgresService>();

        using var provider = services.BuildServiceProvider();
        var bluetoothWorker = provider.GetRequiredService<BluetoothWorker>();
        var postgresService = provider.GetRequiredService<PostgresService>();

        var cts = new CancellationTokenSource();
        Console.CancelKeyPress += (_, e) => { e.Cancel = true; cts.Cancel(); };
        AppDomain.CurrentDomain.ProcessExit += (_, __) => cts.Cancel();

        try
        {
            postgresService.Initialize();

            await Task.WhenAll(
                bluetoothWorker.DoWork(cts.Token)
            );
        }
        finally
        {
            // Ensure graceful shutdown 
            await postgresService.Shutdown();
        }
    }
}