

public class Program
{
    public static async Task Main(string[] args)
    {
        var app = new App();
        await app.RunAsync(args);
    }
}