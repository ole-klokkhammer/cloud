exit_after_auth = false
pid_file = "/tmp/agent.pid"

vault {
  address = "http://vault.home.lan:8200"
}

auto_auth {

  method {
    type = "token_file"

    config {
      token_file_path = "/etc/vault.d/.vault-token"
    }
  }
}

template {
  source      = "/etc/vault.d/templates/homeassistant.ctmpl"
  destination = "/etc/secrets/homeassistant.env"
}