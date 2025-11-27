"use client";

import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { useRouter } from "next/router";

export default function Login() {
  const router = useRouter();
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

    const google_sub = data.user.sub;

    const userRes = await fetch("http://localhost:5000/api/users/get/hasUser", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(google_sub),
      credentials: "include",
    });

    const userData = await userRes.json();
    const hasUser = userData.hasUser;

    if (!hasUser) {
      router.push("/regist")
    } else {
      router.push("/");
    }
  };

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <div className="flex flex-col items-center justify-center h-screen">
        <GoogleLogin onSuccess={handleSuccess} onError={() => console.log("Login Failed")} />
      </div>
    </GoogleOAuthProvider>
  );
}
