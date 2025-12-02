"use client";

import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface UserPayload {
  sub: string;
  name: string;
  email: string;
  isTeacher: boolean;
  exp: number;
}

export default function Header() {
  const [user, setUser] = useState<UserPayload | null>(null);
  const router = useRouter();

  const checkLogin = () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const decoded = jwtDecode<UserPayload>(token);
        // 有効期限チェック (expは秒単位、Date.now()はミリ秒単位)
        if (decoded.exp * 1000 < Date.now()) {
          localStorage.removeItem("token");
          setUser(null);
        } else {
          setUser(decoded);
        }
      } catch (error) {
        console.error("Invalid token:", error);
        localStorage.removeItem("token");
        setUser(null);
      }
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    checkLogin();

    // カスタムイベントをリッスン
    const handleAuthChange = () => {
      checkLogin();
    };

    window.addEventListener("auth-change", handleAuthChange);
    return () => {
      window.removeEventListener("auth-change", handleAuthChange);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.dispatchEvent(new Event("auth-change"));
    router.push("/login");
  };

  return (
    <header className="fixed w-full top-0 h-16 bg-red-100 shadow-lg z-50 flex items-center justify-end px-6">
      <img src="/OICLOG.svg" alt="OIC Logo" className="h-10 mr-auto" />
      <nav>
        <ul className="flex gap-6 text-2xl items-center">
          <li>
            <Link href="/" className="hover:text-blue-600 bg-red-300 px-2 py-1 rounded">
              ホーム
            </Link>
          </li>
          <li>
            {user ? (
              <div className="flex gap-4 items-center">
                <span className="text-lg font-bold">{user.name}</span>
                <button onClick={handleLogout} className="buttonUnderline hover:text-blue-600 bg-red-300 px-2 py-1 rounded text-base">
                  ログアウト
                </button>
              </div>
            ) : (
              <Link href="/login" className="buttonUnderline hover:text-blue-600 bg-red-300 px-2 py-1 rounded">
                ログイン
              </Link>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
}
