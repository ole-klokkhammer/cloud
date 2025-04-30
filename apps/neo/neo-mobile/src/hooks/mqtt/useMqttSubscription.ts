import { useEffect } from 'react';
import { useMqttClient } from '@/context/mqtt.context';

export function useMqttSubscription(topic: string, onMessage: (topic: string, message: Buffer) => void) {
    const client = useMqttClient();

    const onMessageHandler = (topic: string, message: Buffer) => {
        console.log('Received message:', topic, message.toString());
        onMessage(topic, message);
    };

    useEffect(() => {
        client.on('message', onMessageHandler);
        client.subscribe(topic, (err) => {
            if (err) {
                console.error('Failed to subscribe to topic:', topic, err);
            } else {
                console.log('Subscribed to topic:', topic);
            }
        });
        return () => {
            client.off('message', onMessageHandler);
            client.unsubscribe(topic);
        };
    }, [topic]);
}
