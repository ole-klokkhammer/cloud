using System;
using System.Net.Http;
using System.ServiceModel.Syndication;
using System.Threading.Tasks;
using System.Xml;
using System.Text.Json;

class Program
{
    private static readonly HttpClient http = new HttpClient();

    private const int LidarrQualityProfile = 3; // lossless

    private const string LidarrRootFolder = "/music";

    static async Task Main()
    {
        string rssUrl = AppEnvironment.RssUrl; // https://rss.marketingtools.apple.com/api/v2/no/music/most-played/100/albums.rss

        using var reader = XmlReader.Create(rssUrl);
        var feed = SyndicationFeed.Load(reader);

        foreach (var item in feed.Items)
        {
            string artist = item.Authors.Count > 0 ? item.Authors[0].Name : "";
            string album = item.Title.Text;

            Console.WriteLine($"Found: {album} by {artist}");

            string mbid = await LookupMusicBrainzArtist(artist);
            if (!string.IsNullOrEmpty(mbid))
            {
                await AddArtistToLidarr(mbid);
            }
        }
    }

    static async Task<string> LookupMusicBrainzArtist(string artist)
    {
        string url = $"https://musicbrainz.org/ws/2/artist/?query={Uri.EscapeDataString(artist)}&fmt=json";
        var resp = await http.GetStringAsync(url);
        using var doc = JsonDocument.Parse(resp);
        if (doc.RootElement.TryGetProperty("artists", out var artists) && artists.GetArrayLength() > 0)
        {
            return artists[0].GetProperty("id").GetString();
        }
        return null;
    }

    static async Task AddArtistToLidarr(string mbid)
    {
        var payload = new
        {
            foreignArtistId = mbid,
            qualityProfileId = LidarrQualityProfile,
            rootFolderPath = LidarrRootFolder,
            monitored = true,
            addOptions = new { monitor = "all" }
        };

        var content = new StringContent(JsonSerializer.Serialize(payload),
                                        System.Text.Encoding.UTF8,
                                        "application/json");

        var resp = await http.PostAsync($"{AppEnvironment.LidarrUrl}/api/v1/artist?apikey={AppEnvironment.LidarrApiKey}", content);
        Console.WriteLine($"Lidarr response: {resp.StatusCode}");
    }
}
