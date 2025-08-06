
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Hosting;

public class App
{
    public async Task RunAsync(string[] args)
    {
        var host = Host.CreateDefaultBuilder(args)
            .ConfigureServices((context, services) =>
            {
                services.AddLogging(builder =>
                {
                    builder.AddSimpleConsole(options =>
                    {
                        options.TimestampFormat = "[yyyy-MM-dd HH:mm:ss] ";
                        options.IncludeScopes = false;
                    });
                    builder.SetMinimumLevel(AppEnvironment.LogLevel == "debug" ? LogLevel.Debug : LogLevel.Information);
                });
                services.AddSingleton<JsonUtil>();
                services.AddSingleton<HomeassistantService>();
                services.AddSingleton<AirthingsRepository>();
                services.AddSingleton<BluetoothRepository>();
                services.AddSingleton<RabbitMqService>();
                services.AddSingleton<PostgresService>();
                services.AddSingleton<MqttService>();

                services.AddHostedService(provider => provider.GetRequiredService<PostgresService>());
                services.AddHostedService(provider => provider.GetRequiredService<MqttService>());
                services.AddHostedService<BluetoothScanConsumer>();
                services.AddHostedService<AirthingsBatteryConsumer>();
                services.AddHostedService<AirthingsSensorConsumer>();
            })
            .Build();

        await host.RunAsync();
    }
}