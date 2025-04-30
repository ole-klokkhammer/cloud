
export const environment = {
    mqttHost: '192.168.10.207',
    mqttProtocol: 'ws',
    mqttPort: 8000,
    mqttPath: 'mqtt',
    mqttClientPrefix: 'client-',
    mqttReconnectPeriod: 2000,
    getMqttBrokerUrl: () => `${environment.mqttProtocol}://${environment.mqttHost}:${environment.mqttPort}/${environment.mqttPath}`,
    getMqttClientId: (clientId: string) => `${environment.mqttClientPrefix}${clientId}`,
};

