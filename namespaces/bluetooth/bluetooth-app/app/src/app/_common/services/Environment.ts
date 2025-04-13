import { ThisApi } from "../api/this";

export type EnvironmentValues = {
    mqttServer: string;
};

export class Environment {
    private static instance: Environment; // Singleton instance
    private envValues: EnvironmentValues | null = null;

    private constructor() { } // Private constructor to enforce singleton

    // Singleton pattern to ensure only one instance
    public static getInstance(): Environment {
        if (!Environment.instance) {
            Environment.instance = new Environment();
        }
        return Environment.instance;
    }

    // Load environment values from the API
    public async loadEnv(): Promise<EnvironmentValues> {
        if (this.envValues) {
            return this.envValues; // Return cached values if already loaded
        }

        const res = await ThisApi.fetchEnv();
        this.envValues = res; // Cache the loaded values
        return this.envValues;
    }

    // Get a specific environment value by key
    public get(key: keyof EnvironmentValues): string {
        if (!this.envValues) {
            throw new Error("Environment values have not been loaded yet. Call loadEnv() first.");
        }
        return this.envValues[key];
    }

    // Get all environment values
    public getAll(): EnvironmentValues {
        if (!this.envValues) {
            throw new Error("Environment values have not been loaded yet. Call loadEnv() first.");
        }
        return this.envValues;
    }
}