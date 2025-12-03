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
        const currentTime = Date.now();
        const expTime = decoded.exp * 1000;

        if (expTime < currentTime) {
          localStorage.removeItem("token");
          setUser(null);
        } else {
          setUser(decoded);
        }
      } catch (error) {
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

    // 他のタブでの変更を検知
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "token") {
        checkLogin();
      }
    };

    window.addEventListener("auth-change", handleAuthChange);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("auth-change", handleAuthChange);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.dispatchEvent(new Event("auth-change"));
    router.push("/login");
  };

  return (
    <header className="fixed w-full top-0 z-50 bg-red-100 shadow-lg flex flex-col">
      <div className="headerTop flex items-center justify-between px-6 h-16 w-full">
        <img src="/OICLOG.svg" alt="OIC Logo" className="h-10" />
        <nav>
          <ul className="flex gap-6 text-2xl items-center">
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
      </div>
      <div className="headerBottom w-full">
        <nav className="flex gap-8 text-2xl h-12 shadow font-bold items-center justify-center bg-blue-300">
          <Link href="/" className="hover:text-blue-600">
            ホーム
          </Link>
          <Link href="/time-table">
            <button className="hover:text-blue-600">時間割</button>
          </Link>
          <Link href="/attendance">
            <button className="hover:text-blue-600">出席管理</button>
          </Link>
          <Link href="/tasks">
            <button className="hover:text-blue-600">実習課題管理</button>
          </Link>
          <Link href="/events">
            <button className="hover:text-blue-600">イベント情報</button>
          </Link>
          <Link href="/career">
            <button className="hover:text-blue-600">キャリア支援</button>
          </Link>
          <Link href="/community">
            <button className="hover:text-blue-600">コミュニティ</button>
          </Link>
          <Link href="/ai-support">
            <button className="hover:text-blue-600">AI学習支援</button>
          </Link>
        </nav>
      </div>
    </header>
  );
}
