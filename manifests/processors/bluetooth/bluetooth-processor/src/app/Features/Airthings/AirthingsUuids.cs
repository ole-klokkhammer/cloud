public static class BleAirthingsConstants
{
    public const string ManufacturerId = "820";
    
    public static class Services
    {
        public const string DeviceInfo = "0000180a-0000-1000-8000-00805f9b34fb";
        public const string SensorData = "b42e1c08-ade7-11e4-89d3-123b93f75cba";
    }

    public static class Characteristics
    {
        public const string CurrentSensorValue = "b42e2a68-ade7-11e4-89d3-123b93f75cba";

        public static class DeviceInfo
        {
            public const string SystemId = "00002a23-0000-1000-8000-00805f9b34fb";
            public const string FirmwareRevision = "00002a26-0000-1000-8000-00805f9b34fb";
            public const string HardwareRevision = "00002a27-0000-1000-8000-00805f9b34fb";
            public const string SerialNumber = "00002a25-0000-1000-8000-00805f9b34fb";
            public const string ModelNumber = "00002a24-0000-1000-8000-00805f9b34fb";
            public const string ManufacturerName = "00002a29-0000-1000-8000-00805f9b34fb";
        }
    }


}