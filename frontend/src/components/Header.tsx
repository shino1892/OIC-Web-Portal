"use client";

import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Link from "next/link";
import { useRouter } from "next/navigation";
import MajorSelectionModal from "./MajorSelectionModal";

interface UserPayload {
  sub: string;
  name: string;
  email: string;
  isTeacher: boolean;
  exp: number;
}

export default function Header() {
  const [user, setUser] = useState<UserPayload | null>(null);
  const [showMajorModal, setShowMajorModal] = useState(false);
  const [availableMajors, setAvailableMajors] = useState<{ id: number; name: string }[]>([]);
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

  // Check for major selection need
  useEffect(() => {
    if (user && !user.isTeacher) {
      const token = localStorage.getItem("token");
      if (!token) return;

      fetch("/api/users/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => {
          if (res.ok) return res.json();
          // If 404 or other error, ignore (maybe user not fully registered yet)
          return null;
        })
        .then((data) => {
          if (data && data.needs_major_selection) {
            setAvailableMajors(data.available_majors);
            setShowMajorModal(true);
          }
        })
        .catch((err) => console.error("Error checking major:", err));
    }
  }, [user]);

  const handleMajorSelect = async (majorId: number) => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch("/api/users/me/major", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ major_id: majorId }),
      });
      if (res.ok) {
        setShowMajorModal(false);
      } else {
        alert("専攻の登録に失敗しました");
      }
    } catch (error) {
      console.error(error);
      alert("エラーが発生しました");
    }
  };

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
      {showMajorModal && <MajorSelectionModal majors={availableMajors} onSelect={handleMajorSelect} />}
    </header>
  );
}
