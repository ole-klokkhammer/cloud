
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
                services.AddHttpClient();

                services.AddSingleton<JsonUtil>();
                services.AddSingleton<RabbitMqService>();

                services.AddHostedService(sp =>
                {
                    return new RabbitMqForwarder(
                         logger: sp.GetRequiredService<ILogger<RabbitMqForwarder>>(),
                         rabbitMq: sp.GetRequiredService<RabbitMqService>(),
                         httpClient: sp.GetRequiredService<IHttpClientFactory>().CreateClient(),
                         rabbitmqExchange: AppEnvironment.RabbitMqExchange,
                         rabbitmqInbox: AppEnvironment.RabbitMqInbox,
                         httpEndpoint: AppEnvironment.HttpEndpoint
                     );
                });
            })
            .Build();

        await host.RunAsync();
    }
}