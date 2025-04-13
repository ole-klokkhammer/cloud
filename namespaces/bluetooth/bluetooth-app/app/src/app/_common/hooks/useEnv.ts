import { useEffect, useState } from "react";
import { Environment, EnvironmentValues } from "../services/Environment";

export const useEnv = (key: keyof EnvironmentValues) => {
    const [error, setError] = useState<Error | undefined>(undefined);
    const [value, setValue] = useState<string | undefined>(undefined);
    useEffect(() => {
        const service = Environment.getInstance();
        service.loadEnv()
            .then(_ => setValue(service.get(key)))
            .catch(err => setError(err));
    }, [key]);
    return { value, error };
};