
using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client.Events;

public class BluetoothScanConsumer : RabbitMqConsumerBase<BluetoothScanConsumer>
{

    private readonly BluetoothRepository bluetoothRepository;

    public BluetoothScanConsumer(
        JsonUtil json,
        ILogger<BluetoothScanConsumer> logger,
        RabbitMqService rabbitmq,
        BluetoothRepository bluetoothRepository
    ) : base(json, logger, rabbitmq)
    {
        this.bluetoothRepository = bluetoothRepository;
    }

    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "generic.scan.parsed";
    protected override string OutboxRoutingKey => null!;

    protected override async Task OnMessage(object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        var bluetoothScanList = json.Deserialize<List<BluetoothScan>>(message);
        if (bluetoothScanList == null)
        {
            throw new Exception("No data found in payload.");
        }

        logger.LogInformation($"Received Bluetooth scan data with {bluetoothScanList.Count} devices.");
        logger.LogDebug($"Raw JSON: {bluetoothScanList}");
        foreach (var scan in bluetoothScanList)
        {
            await bluetoothRepository.InsertScanAsync(scan);
        }
        logger.LogInformation("Bluetooth scan data processed successfully.");
    }

}