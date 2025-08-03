
using System.Text.Json;
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
                    builder.SetMinimumLevel(LogLevel.Information);
                });
                services.AddSingleton<JsonUtil>();
                services.AddSingleton<HomeassistantService>();
                services.AddSingleton<RabbitMqService>();

                services.AddHostedService<AirthingsSensorConsumer>();
                services.AddHostedService<AirthingsBatteryConsumer>();
            })
            .Build();

        var rabbitMqService = host.Services.GetRequiredService<RabbitMqService>();
        await rabbitMqService.Initialize();

        await host.RunAsync();
    }
}