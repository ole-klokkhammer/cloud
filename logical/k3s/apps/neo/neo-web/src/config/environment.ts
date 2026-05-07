export const environment = {
    keycloak: {
        web: {
            clientId: process.env.KEYCLOAK_CLIENT_ID,
            clientSecret: process.env.KEYCLOAK_CLIENT_SECRET,
            issuer: process.env.KEYCLOAK_ISSUER,
            authSecret: process.env.AUTH_SECRET,
        },
        mobile: {
            clientId: process.env.KEYCLOAK_MOBILE_CLIENT_ID,
            clientSecret: process.env.KEYCLOAK_MOBILE_CLIENT_SECRET,
            authorizeEndpoint: process.env.KEYCLOAK_MOBILE_AUTHORIZE_ENDPOINT,
            tokenEndpoint: process.env.KEYCLOAK_MOBILE_TOKEN_ENDPOINT,
        }
    } 
};