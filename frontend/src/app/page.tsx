// frontend/app/page.tsx
"use client";
// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/Button";
import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>Welcom to OIC!!</h1>
      <Link href="/time-table"><button>時間割</button></Link>
      <Link href="/attendance"><button>出席管理</button></Link>
      <Link href="/tasks"><button>実習課題管理</button></Link>
      <Link href="/events"><button>イベント情報</button></Link>
      <Link href="/career"><button>キャリア支援</button></Link>
      <Link href="/community"><button>コミュニティ</button></Link>
      <Link href="/ai-support"><button>AI学習支援</button></Link>
    </main>
  );
}
