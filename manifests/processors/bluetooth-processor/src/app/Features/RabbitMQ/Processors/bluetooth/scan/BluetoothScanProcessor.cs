
using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

public class BluetoothScanProcessor : RabbitMqProcessorBase<BluetoothScanProcessor>
{

    private readonly BluetoothRepository bluetoothRepository;

    public BluetoothScanProcessor(
        JsonUtil json,
        ILogger<BluetoothScanProcessor> logger,
        RabbitMqService rabbitMqConnectionService,
        BluetoothRepository bluetoothRepository
    ) : base(json, logger, rabbitMqConnectionService)
    {
        this.bluetoothRepository = bluetoothRepository;
    }

    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "generic.scan.raw";
    protected override string OutboxRoutingKey => null!;

    protected override async Task OnMessage(IChannel channel, object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        var bluetoothScanList = json.Deserialize<List<BluetoothScan>>(message);
        if (bluetoothScanList == null)
        {
            throw new ArgumentException("No data found in payload.");
        }

        logger.LogInformation($"Received Bluetooth scan data with {bluetoothScanList.Count} devices.");
        logger.LogDebug($"Raw JSON: {bluetoothScanList}");
        foreach (var scan in bluetoothScanList)
        {
            logger.LogDebug($"Device: {scan.name}, Address: {scan.address}, RSSI: {scan.rssi}");
            await bluetoothRepository.InsertScanAsync(scan);
        }
        logger.LogInformation("Bluetooth scan data processed successfully.");
    }

}