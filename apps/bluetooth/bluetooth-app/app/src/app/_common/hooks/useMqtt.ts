import { useEffect, useState } from "react";
import mqtt, { MqttClient } from "mqtt";

type MqttMessage = {
    topic: string;
    message: string;
};

export const useMqtt = (brokerUrl: string, topic: string) => {
    const [messages, setMessages] = useState<MqttMessage[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [client, setClient] = useState<MqttClient | null>(null);

    useEffect(() => {
        const mqttClient = mqtt.connect(brokerUrl);

        setClient(mqttClient);

        mqttClient.on("connect", () => {
            console.log("Connected to MQTT broker");

            // Subscribe to the topic
            mqttClient.subscribe(topic, (err) => {
                if (err) {
                    console.error("Failed to subscribe to topic:", err);
                    setError(err);
                } else {
                    console.log(`Subscribed to topic: ${topic}`);
                }
            });
        });

        mqttClient.on("message", (receivedTopic, message) => {
            if (receivedTopic === topic) {
                setMessages((prevMessages) => [
                    ...prevMessages,
                    { topic: receivedTopic, message: message.toString() },
                ]);
            }
        });

        mqttClient.on("error", (err) => {
            console.error("MQTT error:", err);
            setError(err);
        });

        mqttClient.on("close", () => {
            console.log("MQTT connection closed");
        });

        // Cleanup on component unmount
        return () => {
            mqttClient.end(true); // Disconnect the client
            setClient(null);
            setError(null);
            setMessages([]);
        };
    }, [brokerUrl, topic]);

    return { messages, client, error };
};