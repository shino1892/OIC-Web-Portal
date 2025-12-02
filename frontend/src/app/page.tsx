"use client";
import React from "react";
import "./globals.css";

// frontend/app/page.tsx
// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/Button";
import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>Welcom to OIC!!</h1>
      <nav className="flex gap-8 text-2xl h-16 shadow font-bold items-center justify-center bg-blue-300">
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
    </main>
  );
}
