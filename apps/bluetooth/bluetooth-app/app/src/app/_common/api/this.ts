"use client";

import { EnvironmentResponse } from "@/app/api/config/route";

async function fetchEnv(): Promise<EnvironmentResponse> {
    const res = await fetch(window.location.origin + "/api/config");
    if (!res.ok) {
        throw new Error("Failed to fetch environment variables");
    }
    return res.json();
}

export const ThisApi = {
    fetchEnv
};