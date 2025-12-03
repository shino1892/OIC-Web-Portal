"use client";

import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { useRouter } from "next/navigation";

export default function Login() {
  const router = useRouter();
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  if (!clientId) {
    console.error("Google Client ID is missing");
    return <div className="flex justify-center items-center h-screen text-red-500">Google Client ID is not configured.</div>;
  }

  const handleSuccess = async (credentialResponse: any) => {
    const token = credentialResponse.credential;
    // Flaskにトークンを送る
    const res = await fetch("/api/users/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
      credentials: "include",
    });

    const data = await res.json();
    console.log("ログイン結果:", data);

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      // ログイン成功時にイベントを発火してヘッダーに通知
      window.dispatchEvent(new Event("auth-change"));
    }

    router.push("/");
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <GoogleLogin onSuccess={handleSuccess} onError={() => console.log("Login Failed")} />
    </div>
  );
}
