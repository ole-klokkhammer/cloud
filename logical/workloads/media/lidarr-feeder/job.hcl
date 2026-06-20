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


    constraint {
      attribute = "${meta.machine}"
      operator  = "="
      value     = "core"
    }

    restart {
      attempts = 0
      mode     = "fail"
    }

    task "lidarr-feeder" {
      driver = "podman"

      config {
        image       = "registry.linole.org/lidarr-feeder:1.0.36"
        force_pull  = true
      }

      env {
        RSS_URL    = "https://rss.marketingtools.apple.com/api/v2/no/music/most-played/100/albums.rss"
      }

      template {
        destination = "secrets/env"
        env         = true
        data = <<EOH
{{ with nomadVar "nomad/jobs" }}
LIDARR_API_KEY={{ .lidarr_api_key }}
{{ end }}
EOH
      }
    }
  }
}