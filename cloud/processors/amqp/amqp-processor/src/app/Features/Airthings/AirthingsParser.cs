
public static class AirthingsParser
{

    public static AirthingsSensor ParseSensor(this GattRoot data, string mac, string? locationId = null)
    {
        if (data == null)
        {
            throw new ArgumentException("No data found in payload.");
        }

        var airthingsDevice = data.ParseDeviceInfo();
        var airthingsSensorData = data.ParseSensorData();

        return new AirthingsSensor
        {
            Mac = mac,
            LocationId = locationId,
            DeviceInfo = airthingsDevice,
            SensorData = airthingsSensorData,
        };
    }

    private static AirthingsSensorData ParseSensorData(this GattRoot data)
    {
        var service = data.Services.FirstOrDefault(s => s.Key == BleAirthingsConstants.Services.SensorData);
        if (service.Value == null)
        {
            throw new ArgumentException("Service not found in data.");
        }

        var characteristic = service.Value.Characteristics
            .FirstOrDefault(c => c.Key == BleAirthingsConstants.Characteristics.CurrentSensorValue);

        if (characteristic.Value == null)
        {
            throw new ArgumentException("Characteristic not found in service.");
        }

        var hexValue = characteristic.Value.Value.Hex;
        var byteArray = HexUtils.ToByteArray(hexValue);
        var value = ByteUtils.Unpack4B8H(byteArray);

        return new AirthingsSensorData
        {
            Humidity = value[1] / 2.0,
            Illuminance = (int)(value[2] / 255.0 * 100),
            Radon1DayAverage = value[4],
            RadonLongTermAverage = value[5],
            Temperature = value[6] / 100.0,
            Pressure = value[7] / 50.0,
            Co2 = value[8] * 1.0,
            Voc = value[9] * 1.0
        };
    }

    private static AirthingsDevice ParseDeviceInfo(this GattRoot data)
    {
        var service = data.Services.FirstOrDefault(s => s.Key == BleAirthingsConstants.Services.DeviceInfo);
        if (service.Value == null)
        {
            throw new ArgumentException("Service not found in data.");
        }

        var systemId = service.GetCharacteristicValue(BleAirthingsConstants.Characteristics.DeviceInfo.SystemId);
        var hardwareRevision = service.GetCharacteristicValue(BleAirthingsConstants.Characteristics.DeviceInfo.HardwareRevision);
        var serial = service.GetCharacteristicValue(BleAirthingsConstants.Characteristics.DeviceInfo.SerialNumber);
        var modelNumber = service.GetCharacteristicValue(BleAirthingsConstants.Characteristics.DeviceInfo.ModelNumber);
        var manufacturerName = service.GetCharacteristicValue(BleAirthingsConstants.Characteristics.DeviceInfo.ManufacturerName);
        var firmwareRevision = service.GetCharacteristicValue(BleAirthingsConstants.Characteristics.DeviceInfo.FirmwareRevision);

        return new AirthingsDevice
        {
            Serial = int.Parse(serial!),
            ModelNumber = int.Parse(modelNumber!),
            ManufacturerName = manufacturerName!,
            HardwareRevision = hardwareRevision!,
            FirmwareRevision = firmwareRevision!,
        };
    }

    public static float ParseBatteryVolt(this byte[] payload)
    {
        var cmd = payload.Take(1).ToArray();
        var data = ByteUtils.UnpackL2BH2B9H(payload.Skip(2).ToArray());
        return (float)((ushort)data[13] / 1000.0);
    }

    public static int ParseBatteryPercentage(this float voltage)
    {
        return (int)Math.Round(TwoBatteries(voltage));
    }

    private static float TwoBatteries(float voltage)
    {
        if (voltage >= 3.00f)
            return 100;
        if (voltage >= 2.80f && voltage < 3.00f)
            return Interpolate(voltage, (2.80f, 3.00f), (81, 100));
        if (voltage >= 2.60f && voltage < 2.80f)
            return Interpolate(voltage, (2.60f, 2.80f), (53, 81));
        if (voltage >= 2.50f && voltage < 2.60f)
            return Interpolate(voltage, (2.50f, 2.60f), (28, 53));
        if (voltage >= 2.20f && voltage < 2.50f)
            return Interpolate(voltage, (2.20f, 2.50f), (5, 28));
        if (voltage >= 2.10f && voltage < 2.20f)
            return Interpolate(voltage, (2.10f, 2.20f), (0, 5));
        return 0;
    }

    private static float Interpolate(float voltage, (float, float) voltageRange, (int, int) percentageRange)
    {
        return (voltage - voltageRange.Item1) / (voltageRange.Item2 - voltageRange.Item1) *
               (percentageRange.Item2 - percentageRange.Item1) + percentageRange.Item1;
    }
}