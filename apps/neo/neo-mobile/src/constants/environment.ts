import { v4 as uuidv4 } from 'uuid';

export const environment = {
    keycloak: {
        clientId: 'neo-mobile-dev',
        issuer: 'https://auth.linole.org/realms/neo',
        redirectUrl: 'com.olklokk.neomobile://*',
        scopes: ['openid', 'profile'],
    },
    mqtt: {
        host: 'broker.linole.org', // '192.168.10.207',
        protocol: 'wss',
        port: 443,
        path: 'mqtt',
        clientId: 'client-' + uuidv4(), // todo
        reconnectPeriod: 2000,
        getBrokerUrl: () => `${environment.mqtt.protocol}://${environment.mqtt.host}:${environment.mqtt.port}/${environment.mqtt.path}`,
        keepalive: 20,
    }
};

