import NextAuth from 'next-auth';
import { authConfig } from './auth.config';
import Keycloak from "next-auth/providers/keycloak"
import { environment } from '@/config/environment';

export const { handlers, auth, signIn, signOut } = NextAuth({
    ...authConfig,
    providers: [
        Keycloak({
            clientId: environment.keycloak.web.clientId,
            clientSecret: environment.keycloak.web.clientSecret,
            issuer: environment.keycloak.web.issuer,
        }),
    ],
    secret: environment.keycloak.web.authSecret,
    trustHost: true
});