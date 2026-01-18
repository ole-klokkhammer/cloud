job "matrix-backup-bot" {
  datacenters = ["dc1"]
  type        = "service"
  
  constraint {
    attribute = "${meta.workload}"
    operator  = "="
    value     = "stateless"
  } 

  group "bot" {
    count = 1 

    task "bot" {
      driver = "docker"

      config {
        image = "container-registry.home.lan:5000/matrix-backup-bot:latest" 
      } 

      template {
        data = <<EOH
{{ with nomadVar "nomad/jobs/matrix/backup-bot" }}
MATRIX_SERVER={{ .MATRIX_SERVER }}
MATRIX_USER={{ .MATRIX_USER }}
MATRIX_PASSWORD={{ .MATRIX_PASSWORD }}
MATRIX_ROOM={{ .MATRIX_ROOM }}
{{ end }}
EOH
        destination = "secrets/bot.env"
        env         = true
      }

      resources {
        cpu    = 100
        memory = 128
      }
    }
  }
}
