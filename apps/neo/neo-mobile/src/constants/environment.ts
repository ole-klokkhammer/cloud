import { v4 as uuidv4 } from 'uuid';

export const environment = {
    mqttHost: 'broker.linole.org', // '192.168.10.207',
    mqttProtocol: 'wss',
    mqttPort: 443,
    mqttPath: 'mqtt',
    mqttClientId: 'client-' + uuidv4(),
    mqttReconnectPeriod: 2000,
    getMqttBrokerUrl: () => `${environment.mqttProtocol}://${environment.mqttHost}:${environment.mqttPort}/${environment.mqttPath}`,
};

