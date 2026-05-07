import { useEffect } from 'react';
import { useMqttClient } from '@/context/mqtt/context';

export function useMqttSubscription(topic: string, onMessage: (topic: string, message: Buffer) => void) {
    const client = useMqttClient();

    const onMessageHandler = (current_topic: string, message: Buffer) => { 
        const hasWildcard = topic.includes('+') || topic.includes('#');

        if (hasWildcard) {
            // If the topic has wildcards, match using a regex
            const regex = new RegExp(
                '^' +
                topic
                    .replace(/\+/g, '[^/]+') // Replace '+' with a single-level wildcard
                    .replace(/#/g, '.*') // Replace '#' with a multi-level wildcard
                    .replace(/\//g, '\\/') + // Escape slashes
                '$'
            );

            if (regex.test(current_topic)) {
                onMessage(current_topic, message);
            }
        } else {
            // If no wildcards, match the topic directly
            if (current_topic === topic) {
                onMessage(current_topic, message);
            }
        }
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
            console.log('Unsubscribed from topic:', topic);
        };
    }, [topic]);
}
