public class HexUtils
{
    public static byte[] ToByteArray(string hex)
    {
        if (string.IsNullOrEmpty(hex))
            return Array.Empty<byte>();

        int length = hex.Length;
        byte[] bytes = new byte[length / 2];
        for (int i = 0; i < length; i += 2)
        {
            bytes[i / 2] = Convert.ToByte(hex.Substring(i, 2), 16);
        }
        return bytes;
    }
}