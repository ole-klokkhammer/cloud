"use client"

import { signIn } from "next-auth/react"

export default function SignInButton() {
    return <button
        className="bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all"
        onClick={() => signIn("keycloak")}>Sign In</button>
}