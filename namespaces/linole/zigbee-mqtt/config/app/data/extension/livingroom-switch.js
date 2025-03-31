class LivingroomSwitchExtension {
    constructor(zigbee, mqtt, state, publishEntityState, eventBus, settings, logger) {
        this.zigbee = zigbee;
        this.mqtt = mqtt;
        this.state = state;
        this.publishEntityState = publishEntityState;
        this.eventBus = eventBus;
        this.settings = settings;
        this.logger = logger;

        logger.info('Loaded  LivingroomSwitchExtension');
    }

    /**
     * This method is called by the controller once Zigbee2MQTT has been started.
     */
    start() {
        this.mqtt.publish('extensions/livingroomswitch', 'hello from LivingroomSwitchExtension');
        // All possible events can be seen here: https://github.com/Koenkk/zigbee2mqtt/blob/dev/lib/eventBus.ts
        this.eventBus.onMQTTMessagePublished(this, (data) => {
            if(data.topic === "zigbee2mqtt/livingroom_switch")  {
                this.mqtt.publish('extensions/livingroomswitch/match', 'hello ' + data.payload);
            }
        });
    }

    /**
     * Is called once the extension has to stop
     */
    stop() {
        this.eventBus.removeListenersExtension(this);
    }
}

module.exports = LivingroomSwitchExtension;
