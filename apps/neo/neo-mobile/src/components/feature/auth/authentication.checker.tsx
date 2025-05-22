import { useAuth } from "@/context/auth/context";
import { router } from "expo-router";
import { useEffect } from "react";

export const AuthenticationChecker = () => {
    const { initializing, authenticated } = useAuth();

    useEffect(() => {
        if (!initializing) {
            if (!authenticated) {
                router.replace('/login');
            } else {
                router.replace('/');
            }
        }
    }, [initializing, authenticated]);

    return null;
}