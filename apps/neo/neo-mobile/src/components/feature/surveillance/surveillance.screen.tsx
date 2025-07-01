
import { AppContainer } from "@/components/ui/container/container";
import { AppText } from "@/components/ui/text/text";
import React, { useEffect, useState } from "react";

export type ChatMessage = {
    id: string;
    text: string;
    sender: 'me' | 'other';
};

export function HomeScreen() {
    return (
        <AppContainer>
            <AppText>Welcome to the Home Screen!</AppText>
        </AppContainer>
    );
}