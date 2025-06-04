public class AirthingsDevice
{
    public int Id { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public int Serial { get; set; }
    public int ModelNumber { get; set; }
    public string Mac { get; set; }
    public string ManufacturerName { get; set; }
    public string HardwareRevision { get; set; }
    public string FirmwareRevision { get; set; }
    public string? LocationId { get; set; }
}

public class AirthingsSensorData
{
    public int Serial { get; set; }
    public double? Temperature { get; set; }
    public double? Humidity { get; set; }
    public double? CO2 { get; set; }
    public double? VOC { get; set; } 
    public double? Pressure { get; set; }
    public int? Illuminance { get; set; }
    public int? Radon1DayAverage { get; set; }
    public int? RadonLongTermAverage { get; set; }

    public string? LocationId { get; set; }
}

public class AirthingsBatteryData
{
    public int Id { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public int Serial { get; set; }
    public int? BatteryLevel { get; set; }
    public int? Voltage { get; set; }
}