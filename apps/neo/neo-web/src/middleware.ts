import NextAuth from 'next-auth';
import { authConfig } from './auth/auth.config';
import { NextRequest, NextResponse } from 'next/server';

function combineMiddleware(...middlewares: Function[]) {
    return async (req: NextRequest) => {
        for (const middleware of middlewares) {
            const result = await middleware(req, NextResponse.next(), () => { });
            if (result instanceof Response || result instanceof NextResponse) {
                return result;
            }
        }
        return NextResponse.next();
    };
}

async function logRequest(req: NextRequest, res: NextResponse) {
    console.log(`My Request URL: ${req.url}`); 
    return NextResponse.next();
}

export default NextAuth(authConfig).auth(logRequest as any);

export const config = {
    // https://nextjs.org/docs/app/building-your-application/routing/middleware#matcher
    matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
};