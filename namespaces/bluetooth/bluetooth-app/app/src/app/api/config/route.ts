import { NextResponse } from "next/server";

type EnvironmentResponse = {
    mqttServer: string;
};


// https://www.wisp.blog/blog/nextjs-15-api-get-and-post-request-examples

export async function GET() {
    // Only expose safe environment variables
    console.log("Fetching environment variables");

    console.log("MQTT Server:", process.env.MQTT_SERVER);
    return NextResponse.json({
        mqttServer: process.env.MQTT_SERVER,
    });
}

export type { EnvironmentResponse }