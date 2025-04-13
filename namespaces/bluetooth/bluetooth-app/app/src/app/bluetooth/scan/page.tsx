"use client";

import {
    Container,
    Typography,
    Box,
    TextField,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Alert,
} from "@mui/material";
import { useMqtt } from "@/app/_common/hooks/useMqtt";
import { useState } from "react";
import {
} from "@mui/material";
import { CollapsibleJson } from "@/app/_common/components/collapsible_json";
import { useEnv } from "@/app/_common/hooks/useEnv";

export default function MqttSubscriptionPage() {
    const { value: mqttServer } = useEnv("mqttServer");

    const defaultTopic = "homeassistant/#";
    const [subscriptionTopic, setSubscriptionTopic] = useState(defaultTopic);
    const { messages, error } = useMqtt(mqttServer!, subscriptionTopic);

    const isValidJson = (str: string) => {
        try {
            JSON.parse(str);
            return true;
        } catch (_) {
            return false;
        }
    };

    const handleTopicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSubscriptionTopic(e.target.value);
    };

    return (
        <Container maxWidth={false} sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                MQTT Topic Subscription on server: <strong>{mqttServer}</strong>
            </Typography>
            <Box sx={{ mb: 4 }}>
                <TextField
                    fullWidth
                    label="Enter Topic"
                    variant="outlined"
                    value={subscriptionTopic}
                    onChange={handleTopicChange}
                    sx={{ mb: 2 }}
                />
                <Typography variant="h6">
                    Subscribed to topic: <strong>{subscriptionTopic}</strong>
                </Typography>
            </Box>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error.message}
                </Alert>
            )}
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Topic</TableCell>
                            <TableCell>Payload</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {messages.map(({ message, topic }, index) => (
                            <TableRow key={index}>
                                <TableCell>{topic}</TableCell>
                                <TableCell>
                                    {isValidJson(message) ? (
                                        <CollapsibleJson data={JSON.parse(message)} />
                                    ) : (
                                        <pre>{message}</pre>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Container>
    );
}

