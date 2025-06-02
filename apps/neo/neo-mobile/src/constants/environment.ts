import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';

export const environment = {
    keycloak: {
        authorizeEndpoint: 'https://neo.linole.org/api/auth/mobile',//'http://localhost:3000/api/auth/mobile',
        tokenEndpoint: 'https://neo.linole.org/api/auth/mobile',//'http://localhost:3000/api/auth/mobile',
        scheme: 'com.olklokk.neomobile://*',
        scopes: ['openid', 'profile'],
    },
    mqtt: {
        host: 'broker.linole.org', // '192.168.10.207',
        protocol: 'wss', // ws
        port: 443, // 8000
        path: 'mqtt',
        clientId: 'client-' + uuidv4(), // TODO
        reconnectPeriod: 2000,
        getBrokerUrl: () => `${environment.mqtt.protocol}://${environment.mqtt.host}:${environment.mqtt.port}/${environment.mqtt.path}`,
        keepalive: 20,
    }
};

