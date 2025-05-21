import { environment } from '@/config/environment';
import { NextResponse } from 'next/server';

export async function GET(req: Request) {
    const { searchParams } = new URL(req.url);

    const redirect_uri = searchParams.get('redirect_uri');
    const codeChallenge = searchParams.get('code_challenge');
    const codeChallengeMethod = searchParams.get('code_challenge_method');

    const url = new URL(environment.keycloak.mobile.authorizeEndpoint!);
    url.searchParams.append('client_id', environment.keycloak.mobile.clientId!);
    url.searchParams.append('redirect_uri', redirect_uri!);
    url.searchParams.append('response_type', 'code');
    url.searchParams.append('scope', 'openid profile');
    url.searchParams.append('code_challenge', codeChallenge!);
    url.searchParams.append('code_challenge_method', codeChallengeMethod!);

    return NextResponse.redirect(url.toString());
}

export async function POST(req: Request) {
    const { code, code_verifier, redirect_uri } = await req.json();

    if (!code) {
        return NextResponse.json(
            { error: 'Authorization code is required' },
            {
                status: 400,
                headers: accessControlHeaders(),
            }
        );
    }

    try {
        const response = await fetch(environment.keycloak.mobile.tokenEndpoint!, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                client_id: environment.keycloak.mobile.clientId!,
                client_secret: environment.keycloak.mobile.clientSecret!,
                redirect_uri,
                code,
                code_verifier,
            }).toString(),
        });

        if (!response.ok) {
            const error = await response.json();
            return NextResponse.json(
                { error: 'Failed to exchange token', details: error },
                {
                    status: response.status,
                    headers: accessControlHeaders(),
                }
            );
        }

        const data = await response.json();
        return NextResponse.json(data, {
            status: 200,
            headers: accessControlHeaders(),
        });
    } catch (error) {
        console.error('Token exchange error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}

export async function OPTIONS() {
    return NextResponse.json(
        {},
        {
            status: 200,
            headers: accessControlHeaders(),
        }
    );
}

const accessControlHeaders = () => ({
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
});
