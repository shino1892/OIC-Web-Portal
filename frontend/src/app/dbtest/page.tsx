"use client";
import { useEffect, useState } from "react";
import { useAuthFetch } from "../../hooks/useAuthFetch";

export default function Departments() {
  console.log("start");
  const [rows, setRows] = useState([]);
  const authFetch = useAuthFetch();

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const res = await authFetch("/api/users/get/db_test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });

        const data = await res.json();
        console.log("departments:", data);
        setRows(data.departments);
      } catch (error) {
        console.error("Fetch error:", error);
      }
    };

    fetchDepartments();
  }, [authFetch]); // ← 1回だけ実行

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
