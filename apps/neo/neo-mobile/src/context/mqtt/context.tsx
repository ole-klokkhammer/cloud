import React, { createContext, useContext, useEffect, useState } from 'react';
import mqtt, { MqttClient } from 'mqtt';
import { environment } from '@/constants/environment';
import { Loading } from '@/components/ui/loading/loading';
import { Spinner } from '@/components/ui/spinner';

const MqttClientContext = createContext<MqttClient | null>(null);

export type MqttClientProviderProps = {
    children: React.ReactNode;
};

export const MqttClientProvider: React.FC<MqttClientProviderProps> = (props) => {
    const { children } = props;
    const [client, setClient] = useState<MqttClient | null>(null);

    useEffect(() => {
        const mqttClient = mqtt.connect(environment.mqtt.getBrokerUrl(), {
            clientId: environment.mqtt.clientId,
            reconnectPeriod: environment.mqtt.reconnectPeriod,
            keepalive: environment.mqtt.keepalive,
        });
        console.log('Connecting to MQTT broker:', environment.mqtt.getBrokerUrl());

        mqttClient.on('connect', () => {
            console.log('Connected to MQTT broker');
        });

        mqttClient.on('close', () => {
            console.log('MQTT connection closed');
        });

        mqttClient.on('offline', () => {
            console.log('MQTT client is offline');
        });

        mqttClient.on('error', (err) => {
            console.log('MQTT error:', err);
        });

        setClient(mqttClient);

        return () => {
            console.log("Cleaning up MQTT client");
            mqttClient.end();
        };
    }, []);

    if (client == null) {
        return <Spinner />
    } else {
        return (
            <MqttClientContext.Provider value={client}>
                {children}
            </MqttClientContext.Provider>
        );
    }
};

export function useMqttClient(): MqttClient {
    const client = useContext(MqttClientContext);
    if (!client) {
        throw new Error('useMqttClient must be used within MqttClientProvider');
    }
    return client;
}