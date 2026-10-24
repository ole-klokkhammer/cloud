# extensions
* https://docs.hivemq.com/hivemq/latest/extensions/interceptors.html#publish-outbound-interceptor
* push each extension to the assigned extension volume of the hivemq pod:
  * cd hivemq-allow-all-extension && ./build_and_push_to_host.sh
  * cd hivemq-kafka-bridge && ./build_and_push_to_host.sh