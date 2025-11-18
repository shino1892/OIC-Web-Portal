"use client";

import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

export default function Login() {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!;

  const handleSuccess = async (credentialResponse: any) => {
    const token = credentialResponse.credential;
    // Flaskにトークンを送る
    const res = await fetch("http://localhost:5000/api/users/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
      credentials: "include",
    });

    const data = await res.json();
    console.log("ログイン結果:", data);
  };

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <div className="flex flex-col items-center justify-center h-screen">
        <GoogleLogin onSuccess={handleSuccess} onError={() => console.log("Login Failed")} />
      </div>
    </GoogleOAuthProvider>
  );
}
