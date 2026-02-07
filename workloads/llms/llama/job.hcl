job "llama-api" {
  datacenters = ["dc1"]
  type        = "service"

  constraint {
    attribute = "${node.unique.name}"
    operator  = "="
    value     = "gpu-worker-0"
  }

  group "llm" {
    count = 1

    network {
      mode = "host"
      port "http" {
        static = 8080
      }
    }

    volume "models" {
      type      = "host"
      read_only = true
      source    = "llama-models"
    }

    task "server" {
      driver = "docker"

      volume_mount {
        volume      = "models"
        destination = "/models"
      }

      config {
        image = "ghcr.io/ggml-org/llama.cpp:full-cuda"
        network_mode = "host"

        args = [
          "--server",
          "--host", "0.0.0.0",
          "--port", "8080", 
          # "-m", "/models/Devstral-Small-2-24B-Instruct-2512-Q4_K_M.gguf",
          "-m", "/models/MiniMax-M2-Q4_K_M-00001-of-00003.gguf",
          "-n", "1024",
          "-t", "12",
          "--n-gpu-layers", "10",
          "-c", "4096",
          "-b", "512",
          "--temp", "0.15"
        ]
      }

      resources {
        memory = 300000 # disable memory limit
        memory_max = 999999
        device "nvidia/gpu" {
          count = 1
        }
      }

      service {
        name = "llama-api"
        port = "http"
        check {
          type     = "http"
          path     = "/health"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}