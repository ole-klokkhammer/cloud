public class AirthingsSensor
{
    public string Mac { get; set; }
    public string? LocationId { get; set; }
    public AirthingsSensorData SensorData { get; set; }
    public AirthingsDevice DeviceInfo { get; set; }
}

public class AirthingsDevice
{
    public int Serial { get; set; }
    public int ModelNumber { get; set; }
    public string ManufacturerName { get; set; }
    public string HardwareRevision { get; set; }
    public string FirmwareRevision { get; set; }
}

public class AirthingsSensorData
{
    public double? Temperature { get; set; }
    public double? Humidity { get; set; }
    public double? Co2 { get; set; }
    public double? Voc { get; set; }
    public double? Pressure { get; set; }
    public int? Illuminance { get; set; }
    public int? Radon1DayAverage { get; set; }
    public int? RadonLongTermAverage { get; set; }
}

public class AirthingsBatteryData
{
    public string Mac { get; set; }
    public int BatteryLevel { get; set; }
    public float Voltage { get; set; }
}