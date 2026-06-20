job "matrix-ai-bot" {
  datacenters = ["dc1"]
  type        = "service"

  group "ai-bot" {
    count = 1

    restart {
      attempts = 2
      interval = "30s"
      delay    = "15s"
      mode     = "delay"
    }

    service {
      name = "matrix-ai-bot"
      port = "8000" 
      check {
        type     = "tcp"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "ai-bot" {
      driver = "docker"

      config {
        image = "container-registry.linole.org/matrix-ai-bot:latest"
      }

      env {
        MATRIX_SERVER   = "matrix.example.com"
        MATRIX_USER     = "ai-bot"
        MATRIX_PASSWORD  = "your-password-here"
        MATRIX_TOKEN    = ""
        MATRIX_ROOM     = "!your-room-id:matrix.org"
        VLLM_API_URL    = "http://llm.home.lan:8000/v1"
        VLLM_MODEL      = "gemma-4-31b-nvfp4"
        LOG_LEVEL       = "INFO"
      }

      resources {
        cpu    = 500
        memory = 512
      }
    }
  }
}