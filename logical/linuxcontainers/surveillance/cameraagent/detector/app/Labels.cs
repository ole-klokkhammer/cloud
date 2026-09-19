// COCO label names for the class ids we track (payload "label" field).
namespace Detector;

internal static class Labels
{
    private static readonly Dictionary<int, string> Names = new() { [15] = "cat" };

    public static string For(int classId) =>
        Names.TryGetValue(classId, out var n) ? n : $"class_{classId}";
}
