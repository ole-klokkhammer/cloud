job "matrix-backup-bot" {
  datacenters = ["dc1"]
  type        = "service"

  group "bot" {
    count = 1

    network {
      mode = "host"
      port "webhook" { static = 8090 }
    }

    volume "data" {
      type      = "host"
      source    = "backup-bot-data"
      read_only = false
    }

    task "bot" {
      driver = "docker"

      config {
        image = "matrix-backup-bot:latest"
        ports = ["webhook"]
      }

      volume_mount {
        volume      = "data"
        destination = "/data"
      }

      template {
        data = <<EOF
MATRIX_SERVER={{ key "config/matrix/server" }}
MATRIX_ROOM={{ key "config/matrix/backup_room" }}
MATRIX_TOKEN={{ with nomadVar "nomad/jobs/matrix-backup-bot" }}{{ .matrix_token }}{{ end }}
WEBHOOK_PORT=8090
EOF
        destination = "secrets/env"
        env         = true
      }

      resources {
        cpu    = 100
        memory = 128
      }

      service {
        name = "backup-bot"
        port = "webhook"
        tags = ["matrix", "backup", "monitoring"]

        check {
          type     = "http"
          path     = "/health"
          interval = "30s"
          timeout  = "5s"
        }
      }
    }
  }
}
