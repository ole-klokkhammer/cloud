variable "version" {
  type    = string
  default = "latest"
}

variable "log_level" {
  type    = string
  default = "INFO"
}

variable "scan_timeout" {
  type    = string
  default = "60"
}

variable "connect_timeout" {
  type    = string
  default = "60"
}

variable "command_timeout" {
  type    = string
  default = "60"
}

job "hub0-bluetooth-bridge" {
  datacenters = ["dc1"]
  type        = "service"

  constraint {
    attribute = "${meta.machine}"
    operator  = "="
    value     = "hub0"
  }
  
  constraint {
    attribute = "${meta.bluetooth}"
    operator  = "="
    value     = "true"
  }

  group "bridge" {
    count = 1

    network {
      port "health" {}
    }

    restart {
      attempts = 3
      delay    = "10s"
      interval = "1m"
      mode     = "delay"
    }

    task "bridge" {
      driver = "docker"

      config {
        image      = "ghcr.io/ole-klokkhammer/bluetooth-bridge:${var.version}"
        force_pull = true
        ports      = ["health"]
        volumes = [
          "/run/dbus/system_bus_socket:/run/dbus/system_bus_socket"
        ]
      }

      service {
        name     = "bluetooth-bridge"
        provider = "nomad"
        tags     = ["bridge", "bluetooth", "mqtt"]
        port     = "health"

        check {
          name     = "bluetooth-bridge-health"
          type     = "http"
          path     = "/health"
          port     = "health"
          interval = "10s"
          timeout  = "2s"
        }
      }

      env {
        HEALTH_PORT     = "${NOMAD_PORT_health}"
        MQTT_BROKER     = "hivemq.home.lan"
        LOG_LEVEL       = var.log_level
        SCAN_TIMEOUT    = var.scan_timeout
        CONNECT_TIMEOUT = var.connect_timeout
        COMMAND_TIMEOUT = var.command_timeout
      }

      resources {
        cpu    = 200
        memory = 256
      }
    }
  }
}