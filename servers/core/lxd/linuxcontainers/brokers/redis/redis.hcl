job "redis" {
  datacenters = ["dc1"]
  type = "service"

  constraint {
    attribute = "${meta.role}"
    operator  = "="
    value     = "redis"
  }

  group "app" {
    
    network {
      mode = "host"
      port "redis" { 
        to = 6379
      }
    }

    task "redis" {
      driver = "docker"

      config { 
        image = "docker.io/redis:8"
        network_mode = "host"
        ports = ["redis"]
      }

      env {
        TZ = "Europe/Oslo"
      }

      resources {
        cpu    = 200
        memory = 128
      }

      service {
        name = "redis"
        port = "redis"
        provider = "consul"
        check {
          type     = "script"
          command  = "redis-cli"
          args     = ["-h", "localhost", "ping"]
          interval = "30s"
          timeout  = "5s"
        }
      }
    }
  }
}