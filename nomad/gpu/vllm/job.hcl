job "vllm" {
    datacenters = ["dc1"]
    type        = "service"


    # If you DON'T have GPU scheduling, pin the job to gpu-worker-0 like this:
    constraint {
        attribute = "${node.unique.name}"
        value     = "gpu-worker-0"
    }

    group "api" {
        count = 1

        network {
            port "http" {
                to = 8000
            }
        }

        # # Keep model cache between restarts on the client
        # volume "hf_cache" {
        #     type      = "host"
        #     read_only = false
        #     source    = "hf-cache"
        # }

        task "vllm" {
            driver = "docker" 

            env {
                # Set your model here (HF repo id or local path inside the container)
                MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
                HF_HOME  = "/data/hf"
            }

            config {
                image = "vllm/vllm-openai:latest"

                # Pass GPU through to Docker (works if Docker is configured with nvidia runtime)
                runtime_args = ["--gpus=all"]

                ports = ["http"]

                # vLLM args
                args = [
                    "--model", "${MODEL_ID}",
                    "--host", "0.0.0.0",
                    "--port", "8000",
                    "--served-model-name", "default",
                ]

                volumes = [
                    "local:/local",
                    "/home/ubuntu/vllm/cache:/data/hf",
                ]
            }

            service {
                name = "vllm"
                port = "http" 
                check {
                    type     = "http"
                    path     = "/health"
                    interval = "10s"
                    timeout  = "2s"
                }
            }

            logs {
                max_files     = 5
                max_file_size = 50
            }
        } 
    }
}