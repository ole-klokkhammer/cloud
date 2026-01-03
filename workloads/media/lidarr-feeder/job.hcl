job "lidarr-feeder" {
  datacenters = ["dc1"]
  type        = "batch"

  # Run daily at 02:00
  periodic {
    crons            = ["0 2 * * *"]
    prohibit_overlap = true
    time_zone        = "UTC"
  }

  group "lidarr-feeder" {

    restart {
      attempts = 0
      mode     = "fail"
    }

    task "lidarr-feeder" {
      driver = "docker"

      config {
        image       = "ghcr.io/ole-klokkhammer/lidarrfeeder:1.0.36"
        force_pull  = true
      }

      env {
        LIDARR_URL = "http://torrent-stack.home.lan:8686"
        RSS_URL    = "https://rss.marketingtools.apple.com/api/v2/no/music/most-played/100/albums.rss"
      }

      vault {}

      template {
        destination = "secrets/env"
        env         = true
        data        = <<EOH
{{ with secret "kv/data/secret/apps/torrent-stack" -}}
LIDARR_API_KEY={{ .Data.data.LIDARR_API_KEY }}
{{- end }}
EOH
      }
    }
  }
}