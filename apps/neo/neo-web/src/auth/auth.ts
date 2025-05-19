import NextAuth from 'next-auth';
import { authConfig } from './auth.config';
import Keycloak from "next-auth/providers/keycloak"
import { environment } from '@/config/environment';

export const { handlers, auth, signIn, signOut } = NextAuth({
    ...authConfig,
    providers: [
        Keycloak({
            clientId: environment.keycloakClientId,
            clientSecret: environment.keycloakClientSecret,
            issuer: environment.keycloakIssuer,
        }),
    ],
    secret: environment.authSecret,
    trustHost: true
});