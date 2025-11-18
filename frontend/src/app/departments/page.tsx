"use client";
import { useEffect, useState } from "react";

export default function Departments() {
  console.log("start");
  const [rows, setRows] = useState([]);

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/users/get/departments", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
        });

        const data = await res.json();
        console.log("departments:", data);
        setRows(data.departments);
      } catch (error) {
        console.error("Fetch error:", error);
      }
    };

    fetchDepartments();
  }, []); // ← 1回だけ実行

  return (
    <main>
      <h1>departments</h1>

      <ul>
        {rows.map((row: any) => (
          <li key={row.id}>{row.name}</li>
        ))}
      </ul>
    </main>
  );
}
