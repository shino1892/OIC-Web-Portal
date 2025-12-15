"use client";
import React from "react";
import App from  "../components/home";
import ReactDOM from "react-dom/client";
import TimeTable from "../components/Timetable";

import "./globals.css";

// frontend/app/page.tsx
// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/Button";
   
 
export default function Page() {
  return (
    <main>

      <TimeTable />
    </main>
  );
}



