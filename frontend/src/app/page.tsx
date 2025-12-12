"use client";
import React from "react";
import App from  "../components/home";
import ReactDOM from "react-dom/client";
import "./globals.css";

// frontend/app/page.tsx
// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/Button";

export default function Home() {
  return (
    <main>
      <br />
      <App name="ReactTS" />
    </main>
  );
}

