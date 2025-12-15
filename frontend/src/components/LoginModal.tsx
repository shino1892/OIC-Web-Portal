"use client";

import { GoogleLogin } from "@react-oauth/google";
import { useRouter } from "next/navigation";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function LoginModal({ isOpen, onClose }: LoginModalProps) {
  const router = useRouter();
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  if (!clientId) {
    console.error("Google Client ID is missing");
    return null;
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

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      // ログイン成功時にイベントを発火してヘッダーに通知
      window.dispatchEvent(new Event("auth-change"));
    }

    router.push("/");
    onClose(); // モーダルを閉じる
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-[300px] w-full relative flex flex-col items-center">
        <button onClick={onClose} className="absolute top-0 right-2 text-gray-500 hover:text-gray-700">×</button>
        <h2 className="text-xl font-bold mb-4 text-center">ログイン</h2>
        <div className="flex justify-center">
          <GoogleLogin onSuccess={handleSuccess} onError={() => {}} />
        </div>
      </div>
    </div>
  );
}