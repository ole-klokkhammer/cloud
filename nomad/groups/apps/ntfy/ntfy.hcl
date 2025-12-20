job "ntfy" {
  datacenters = ["dc1"]
  type = "service"

  constraint {
    attribute = "${meta.machine}"
    operator  = "="
    value     = "core"
  }

  constraint {
    attribute = "${meta.workload}"
    operator  = "="
    value     = "stateless"
  }

  group "app" {

    network { 
      port "ntfy" { to = 80 }
    }

    task "ntfy" {
      driver = "podman"
      
      config {
        image = "docker.io/binwiederhier/ntfy"
        args  = ["serve"]
        ports = ["ntfy"]
      }
      
      env {
        TZ = "Europe/Oslo"
        #NTFY_CACHE = "redis"
        #NTFY_REDIS_HOST = "redis.service.consul:6379"  # or your Redis address
      }

      resources {
        cpu    = 200
        memory = 128
      }
      
      service {
        name = "ntfy"
        port = "ntfy"
        check {
          type     = "http"
          path     = "/"
          interval = "30s"
          timeout  = "5s"
        }
      }
    }
  }
}