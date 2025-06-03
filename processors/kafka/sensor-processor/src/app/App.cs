
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

        services.AddSingleton<SensorService>();

        using var provider = services.BuildServiceProvider();
        var service = provider.GetRequiredService<SensorService>();

        await service.DoWork();
    }
}