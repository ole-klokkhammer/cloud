using System.IO;

class ByteUtils
{
    public static ushort[] Unpack4B8H(byte[] byteArray)
    {
        // Unpack byteArray as per "<4B8H"
        using (var ms = new MemoryStream(byteArray))
        using (var reader = new BinaryReader(ms))
        {
            ushort[] result = new ushort[12];
            // First 4 bytes as ushorts (cast each byte to ushort)
            for (int i = 0; i < 4; i++)
            {
                result[i] = reader.ReadByte();
            }
            // Next 8 ushorts
            for (int i = 4; i < 12; i++)
            {
                result[i] = reader.ReadUInt16();
            }
            return result;
        }
    }

    public static object[] UnpackL2BH2B9H(byte[] byteArray)
    {
        using (var ms = new MemoryStream(byteArray))
        using (var reader = new BinaryReader(ms))
        {
            var result = new object[15];
            result[0] = reader.ReadUInt32();      // L
            result[1] = reader.ReadByte();        // B
            result[2] = reader.ReadByte();        // B
            result[3] = reader.ReadUInt16();      // H
            result[4] = reader.ReadByte();        // B
            result[5] = reader.ReadByte();        // B
            for (int i = 6; i < 15; i++)
            {
                result[i] = reader.ReadUInt16();  // 9H
            }
            return result;
        }
    }
}