"use client";
import React from "react";
import App from  "../components/home";
import ReactDOM from "react-dom/client";
import TimeTable from "../components/Timetable";
import AttendanceSummary from "../components/Attendance";

import "./globals.css";

// frontend/app/page.tsx
// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/Button";
   
 
export default function Page() {
  return (
    <main className="mx-auto max-w-6xl px-4">
      <div className="grid gap-6 md:grid-cols-2">
        <TimeTable />
        <AttendanceSummary />
      </div>
    </main>
  );
}



