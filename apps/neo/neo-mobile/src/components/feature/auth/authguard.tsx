import { useAuth } from "@/context/auth/context";
import { router } from "expo-router";
import { useEffect } from "react";

export const AuthGuard = () => {
    const { initializing, authenticated } = useAuth();

    useEffect(() => {
        if (!initializing) {
            if (!authenticated) {
                console.log('not authenticated, redirecting to login');
                router.replace('/login');
            }
        }
    }, [initializing, authenticated]);

    return null;
}