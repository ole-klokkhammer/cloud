public class BluetoothScan
{
    public string? name { get; set; }
    public string? address { get; set; }
    public int rssi { get; set; }
    public Dictionary<string, object>? manufacturer_data { get; set; }
}