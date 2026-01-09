"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Link from "next/link";
import { useRouter } from "next/navigation";
import MajorSelectionModal from "./MajorSelectionModal";
import { useAuthFetch } from "@/hooks/useAuthFetch";

interface UserPayload {
  sub: string;
  name: string;
  email: string;
  isTeacher: boolean;
  exp: number;
}

type NotificationItem = {
  id: number;
  type: string;
  message: string;
  scope: "ALL" | "USER" | "DEPARTMENT" | "CLASS" | string;
  is_read: boolean;
  read_at: string | null;
  created_at: string | null;
};

export default function Header() {
  const [user, setUser] = useState<UserPayload | null>(null);
  const [showMajorModal, setShowMajorModal] = useState(false);
  const [availableMajors, setAvailableMajors] = useState<{ id: number; name: string }[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[] | null>(null);
  const [notificationsError, setNotificationsError] = useState<string | null>(null);
  const [markingReadIds, setMarkingReadIds] = useState<Set<number>>(new Set());
  const notificationsRef = useRef<HTMLDivElement | null>(null);
  const router = useRouter();
  const authFetch = useAuthFetch();

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
    setShowNotifications(false);
    window.dispatchEvent(new Event("auth-change"));
    router.push("/login");
  };

  const hasToken = useMemo(() => {
    if (typeof window === "undefined") return false;
    return Boolean(localStorage.getItem("token"));
  }, [user]);

  const fetchNotifications = async () => {
    if (!hasToken) {
      setNotifications([]);
      return;
    }

    try {
      setNotificationsError(null);
      setNotifications(null);
      const res = await authFetch("/api/notifications/?limit=50");
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `HTTP ${res.status}`);
      }
      const data = (await res.json()) as NotificationItem[];
      setNotifications(Array.isArray(data) ? data : []);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setNotificationsError(msg);
      setNotifications([]);
    }
  };

  const markAsRead = async (notificationId: number) => {
    if (!hasToken) return;

    setMarkingReadIds((prev) => {
      const next = new Set(prev);
      next.add(notificationId);
      return next;
    });

    try {
      const res = await authFetch("/api/notifications/read", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notification_id: notificationId }),
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `HTTP ${res.status}`);
      }

      setNotifications((prev) => {
        if (!prev) return prev;
        return prev.map((n) => (n.id === notificationId ? { ...n, is_read: true, read_at: n.read_at ?? new Date().toISOString() } : n));
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setNotificationsError(msg);
    } finally {
      setMarkingReadIds((prev) => {
        const next = new Set(prev);
        next.delete(notificationId);
        return next;
      });
    }
  };

  useEffect(() => {
    if (!showNotifications) return;

    fetchNotifications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showNotifications]);

  useEffect(() => {
    if (!showNotifications) return;

    const onPointerDown = (e: MouseEvent | TouchEvent) => {
      const el = notificationsRef.current;
      if (!el) return;
      if (e.target instanceof Node && el.contains(e.target)) return;
      setShowNotifications(false);
    };

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("touchstart", onPointerDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("touchstart", onPointerDown);
    };
  }, [showNotifications]);

  return (
    <header className="fixed w-full top-0 z-50 bg-red-100 shadow-lg flex flex-col">
      <div className="headerTop flex items-center justify-between px-6 h-16 w-full">
        <img src="/OICLOG.svg" alt="OIC Logo" className="h-10" />
        <nav>
          <ul className="flex gap-6 text-2xl items-center">
            <li>
              {user ? (
                <div className="flex gap-4 items-center" ref={notificationsRef}>
                  <div className="relative">
                    <button type="button" aria-label="通知" onClick={() => setShowNotifications((v) => !v)} className="buttonUnderline hover:text-blue-600 bg-red-300 px-2 py-1 rounded text-base inline-flex items-center">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2Zm6-6V11a6 6 0 0 0-5-5.91V4a1 1 0 1 0-2 0v1.09A6 6 0 0 0 6 11v5l-2 2v1h16v-1l-2-2Z" fill="currentColor" />
                      </svg>
                    </button>

                    {showNotifications && (
                      <div className="absolute right-0 mt-2 w-[22rem] max-w-[80vw] bg-red-100 shadow-lg rounded p-4 text-base">
                        <div className="flex items-center justify-between mb-3">
                          <div className="text-lg font-bold">通知</div>
                          <button type="button" onClick={() => setShowNotifications(false)} className="buttonUnderline hover:text-blue-600 bg-red-300 px-2 py-1 rounded text-sm">
                            閉じる
                          </button>
                        </div>

                        {notificationsError && (
                          <div className="bg-red-100 p-3 rounded mb-3">
                            <div className="font-bold">読み込みに失敗しました</div>
                            <div className="text-sm break-words">{notificationsError}</div>
                          </div>
                        )}

                        {notifications === null ? (
                          <div className="bg-red-100 p-3 rounded">
                            <div>読み込み中...</div>
                          </div>
                        ) : notifications.length === 0 ? (
                          <div className="bg-red-100 p-3 rounded">
                            <div>通知はありません</div>
                          </div>
                        ) : (
                          <ul className="space-y-2 max-h-80 overflow-auto">
                            {notifications.map((n) => (
                              <li key={n.id} className="bg-red-100 p-3 rounded">
                                <div className="flex items-start justify-between gap-3">
                                  <div className="min-w-0">
                                    <div className="text-sm font-bold">
                                      {n.is_read ? "既読" : "未読"} / {n.type}
                                    </div>
                                    <div className={n.is_read ? "text-base" : "text-base font-bold"}>{n.message}</div>
                                    {n.created_at && <div className="text-xs mt-1">作成: {n.created_at}</div>}
                                    {!n.is_read && (
                                      <div className="mt-2">
                                        <button type="button" onClick={() => markAsRead(n.id)} disabled={markingReadIds.has(n.id)} className="buttonUnderline hover:text-blue-600 bg-red-300 px-2 py-1 rounded text-sm disabled:opacity-60">
                                          {markingReadIds.has(n.id) ? "既読中..." : "既読にする"}
                                        </button>
                                      </div>
                                    )}
                                  </div>
                                  <div className="text-xs whitespace-nowrap">#{n.id}</div>
                                </div>
                              </li>
                            ))}
                          </ul>
                        )}

                        <div className="mt-3">
                          <button type="button" onClick={fetchNotifications} className="buttonUnderline hover:text-blue-600 bg-red-300 px-2 py-1 rounded text-sm">
                            更新
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
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
