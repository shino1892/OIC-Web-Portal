"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface TimetableEntry {
  id: number;
  date: string;
  period: number;
  subject_name: string;
  teacher_name: string;
  start_time: string;
  end_time: string;
}

interface SubjectSummary {
  subject_name: string;
  present: number;
  absent: number;
  late: number;
  early: number;
  public_absent: number;
  total: number;
}

interface HistoryEntry {
  date: string;
  period: number;
  subject_name: string;
  status: string;
  reason: string | null;
  marked_at: string;
}

interface AttendanceSummary {
  出席: number;
  欠席: number;
  遅刻: number;
  早退: number;
  公欠: number;
  total: number;
  attendance_rate: number;
  subject_summary: SubjectSummary[];
  recent_history: HistoryEntry[];
}

const PUBLIC_ABSENCE_REASONS = ["入社試験", "会社訪問", "面接", "健康診断", "忌引", "その他"];

export default function AttendancePage() {
  const router = useRouter();
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [summary, setSummary] = useState<AttendanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<number | null>(null);

  // Application Form State
  const [selectedClasses, setSelectedClasses] = useState<number[]>([]);
  const [applicationType, setApplicationType] = useState<string>("公欠");

  // Reason State
  const [reason, setReason] = useState(""); // For text input (normal or 'Other')
  const [selectedReasonType, setSelectedReasonType] = useState<string>(PUBLIC_ABSENCE_REASONS[0]); // For select input

  // Date/Mode State
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [publicAbsenceMode, setPublicAbsenceMode] = useState<"date" | "period">("date");

  const [appMessage, setAppMessage] = useState<string | null>(null);

  const formatDate = (d: Date) => {
    const year = d.getFullYear();
    const month = ("0" + (d.getMonth() + 1)).slice(-2);
    const day = ("0" + d.getDate()).slice(-2);
    return `${year}-${month}-${day}`;
  };

  // Initial Setup
  useEffect(() => {
    const today = formatDate(new Date());
    setStartDate(today);
    setEndDate(today);

    const initFetch = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      try {
        // 1. Get User Info
        const userRes = await fetch("/api/users/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!userRes.ok) throw new Error("Failed to fetch user");
        const userData = await userRes.json();
        setUserId(userData.user_id);

        // 2. Get Summary
        const sumRes = await fetch(`/api/attendance/summary?user_id=${userData.user_id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (sumRes.ok) {
          const sumData = await sumRes.json();
          setSummary(sumData);
        }
      } catch (error) {
        console.error("Error fetching initial data:", error);
      } finally {
        setLoading(false);
      }
    };

    initFetch();
  }, [router]);

  // Sync endDate with startDate when not in Public Absence mode
  useEffect(() => {
    if (applicationType !== "公欠") {
      setEndDate(startDate);
    }
    // Reset selected classes when application type changes
    setSelectedClasses([]);
  }, [applicationType, startDate]);

  // Fetch Timetable when date or userId changes
  useEffect(() => {
    const fetchTimetable = async () => {
      if (!userId || !startDate || !endDate) return;

      const token = localStorage.getItem("token");
      try {
        const ttRes = await fetch(`/api/timetables/?start_date=${startDate}&end_date=${endDate}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (ttRes.ok) {
          const ttData = await ttRes.json();
          setTimetable(ttData);
          // If in "Date" mode for Public Absence, auto-select all
          if (applicationType === "公欠" && publicAbsenceMode === "date") {
            setSelectedClasses(ttData.map((t: TimetableEntry) => t.id));
          }
        }
      } catch (error) {
        console.error("Error fetching timetable:", error);
      }
    };
    fetchTimetable();
  }, [userId, startDate, endDate, applicationType, publicAbsenceMode]);

  const handleClassSelection = (id: number) => {
    if (applicationType === "早退") {
      // Radio behavior: only one selected
      setSelectedClasses([id]);
    } else {
      // Checkbox behavior: toggle
      setSelectedClasses((prev) => {
        if (prev.includes(id)) {
          return prev.filter((item) => item !== id);
        } else {
          return [...prev, id];
        }
      });
    }
  };

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault();

    // Construct final reason
    let finalReason = reason;
    if (applicationType === "公欠") {
      if (selectedReasonType === "その他") {
        if (!reason) {
          setAppMessage("その他の理由を入力してください");
          return;
        }
        finalReason = `公欠(その他): ${reason}`;
      } else {
        finalReason = `公欠: ${selectedReasonType}`;
      }
    } else {
      if (!reason) {
        setAppMessage("理由を入力してください");
        return;
      }
    }

    if (selectedClasses.length === 0) {
      setAppMessage("授業を選択してください (または授業がありません)");
      return;
    }

    const token = localStorage.getItem("token");
    setAppMessage("送信中...");

    try {
      for (const timetableId of selectedClasses) {
        await fetch("/api/attendance/status", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            user_id: userId,
            timetable_id: timetableId,
            status: applicationType,
            reason: finalReason,
          }),
        });
      }
      setAppMessage("申請が完了しました");
      // Reset form slightly?
      if (applicationType !== "公欠") setReason("");

      // Refresh summary
      if (userId) {
        const sumRes = await fetch(`/api/attendance/summary?user_id=${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (sumRes.ok) setSummary(await sumRes.json());
      }
    } catch (error) {
      setAppMessage("エラーが発生しました");
    }
  };

  if (loading) return <div className="p-8 text-center">読み込み中...</div>;

  if (!summary) {
  return <div className="p-8 text-center">データがありません</div>;
}

return (
  <div className="rounded-lg border bg-white shadow-sm">
    {/* 出席サマリー */}
    <div className="rounded-lg border bg-white shadow-sm">
      <div className="border-b p-4">
        <h2 className="text-lg font-semibold">出席状況</h2>
      </div>

      <div className="grid grid-cols-3 divide-x text-center">
        <div className="p-4">
          <p className="text-sm text-gray-600">出席</p>
          <p className="mt-1 text-xl font-semibold">
            {summary.出席}
          </p>
        </div>

        <div className="p-4">
          <p className="text-sm text-gray-600">欠席</p>
          <p className="mt-1 text-xl font-semibold">
            {summary.欠席}
          </p>
        </div>

        <div className="p-4">
          <p className="text-sm text-gray-600">出席率</p>
          <p className="mt-1 text-xl font-semibold">
            {summary.attendance_rate}%
          </p>
        </div>
      </div>
    </div>

    {/* 直近の活動履歴 */}
    <div className="rounded-lg border bg-white shadow-sm">
      <div className="border-b p-4">
        <h2 className="text-lg font-semibold">直近の活動履歴</h2>
      </div>

      {summary.recent_history.length === 0 ? (
        <p className="p-4 text-sm text-gray-500">
          履歴はありません
        </p>
      ) : (
        <div className="divide-y">
          {summary.recent_history.map((h, index) => (
            <div
              key={index}
              className="grid grid-cols-[80px_40px_1fr] items-center p-3 text-sm"
            >
              <div className="text-gray-600">
                {h.date}
              </div>
              <div className="text-center">
                {h.period}限
              </div>
              <div>
                <p className="font-medium">
                  {h.subject_name}
                </p>
                <p className="text-xs text-gray-500">
                  {h.status}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);

}