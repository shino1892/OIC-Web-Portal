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

  return (
    <main className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Summary Section */}
        <section className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4 text-gray-800">出席状況サマリー</h2>
          {summary ? (
            <div className="space-y-6">
              {/* Overall Stats */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-center">
                <div className="p-3 bg-blue-50 rounded">
                  <div className="text-sm text-gray-500">出席</div>
                  <div className="text-2xl font-bold text-blue-600">{summary.出席}</div>
                </div>
                <div className="p-3 bg-red-50 rounded">
                  <div className="text-sm text-gray-500">欠席</div>
                  <div className="text-2xl font-bold text-red-600">{summary.欠席}</div>
                </div>
                <div className="p-3 bg-yellow-50 rounded">
                  <div className="text-sm text-gray-500">遅刻</div>
                  <div className="text-2xl font-bold text-yellow-600">{summary.遅刻}</div>
                </div>
                <div className="p-3 bg-orange-50 rounded">
                  <div className="text-sm text-gray-500">早退</div>
                  <div className="text-2xl font-bold text-orange-600">{summary.早退}</div>
                </div>
                <div className="p-3 bg-green-50 rounded">
                  <div className="text-sm text-gray-500">公欠</div>
                  <div className="text-2xl font-bold text-green-600">{summary.公欠}</div>
                </div>
                <div className={`p-3 rounded ${summary.attendance_rate < 80 ? "bg-red-100" : "bg-gray-100"}`}>
                  <div className="text-sm text-gray-500">出席率</div>
                  <div className={`text-2xl font-bold ${summary.attendance_rate < 80 ? "text-red-600" : "text-gray-700"}`}>{summary.attendance_rate}%</div>
                  {summary.attendance_rate < 80 && <div className="text-xs text-red-500 font-bold mt-1">留年注意</div>}
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Subject Breakdown */}
                <div>
                  <h3 className="font-bold text-gray-700 mb-2">科目別状況</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm text-left text-gray-500">
                      <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                          <th className="px-3 py-2">科目名</th>
                          <th className="px-3 py-2">欠席</th>
                          <th className="px-3 py-2">遅刻</th>
                          <th className="px-3 py-2">出席率</th>
                        </tr>
                      </thead>
                      <tbody>
                        {summary.subject_summary.map((sub, idx) => {
                          const denom = sub.total - sub.public_absent;
                          const rate = denom > 0 ? ((denom - sub.absent) / denom) * 100 : sub.total > 0 ? 100 : 0;

                          return (
                            <tr key={idx} className="bg-white border-b">
                              <td className="px-3 py-2 font-medium text-gray-900">{sub.subject_name}</td>
                              <td className={`px-3 py-2 ${sub.absent > 0 ? "text-red-600 font-bold" : ""}`}>{sub.absent}</td>
                              <td className="px-3 py-2">{sub.late}</td>
                              <td className={`px-3 py-2 ${rate < 80 ? "text-red-600 font-bold" : ""}`}>{rate.toFixed(1)}%</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Recent History */}
                <div>
                  <h3 className="font-bold text-gray-700 mb-2">直近の活動履歴 (出席以外)</h3>
                  {summary.recent_history.length > 0 ? (
                    <ul className="space-y-2">
                      {summary.recent_history.map((hist, idx) => (
                        <li key={idx} className="p-3 bg-gray-50 rounded border border-gray-200 text-sm">
                          <div className="flex justify-between items-start">
                            <div>
                              <span className="font-bold text-gray-800">
                                {hist.date} {hist.period}限
                              </span>
                              <span className="ml-2 text-gray-600">{hist.subject_name}</span>
                            </div>
                            <span
                              className={`px-2 py-0.5 rounded text-xs font-bold 
                              ${hist.status === "欠席" ? "bg-red-100 text-red-700" : hist.status === "遅刻" ? "bg-yellow-100 text-yellow-700" : hist.status === "早退" ? "bg-orange-100 text-orange-700" : "bg-green-100 text-green-700"}`}
                            >
                              {hist.status}
                            </span>
                          </div>
                          {hist.reason && <div className="mt-1 text-gray-500 text-xs">理由: {hist.reason}</div>}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-500">履歴はありません</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <p>データなし</p>
          )}
        </section>

        {/* Application Form */}
        <section className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4 text-gray-800">各種申請</h2>

          <form onSubmit={handleSubmitApplication}>
            {/* 1. Type Selection */}
            <div className="mb-6">
              <h3 className="font-bold text-gray-700 mb-2">1. 申請種別</h3>
              <div className="flex gap-4 flex-wrap">
                {["公欠", "欠席", "遅刻", "早退"].map((type) => (
                  <label key={type} className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="appType" value={type} checked={applicationType === type} onChange={(e) => setApplicationType(e.target.value)} className="w-4 h-4 text-blue-600" />
                    <span>{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* 2. Date & Period Selection */}
            <div className="mb-6">
              <h3 className="font-bold text-gray-700 mb-2">2. 対象日時・授業</h3>

              <div className="flex flex-col gap-4">
                {/* Date Picker */}
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600">{applicationType === "公欠" ? "開始日:" : "日付:"}</label>
                  <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="p-2 border rounded" />

                  {applicationType === "公欠" && (
                    <>
                      <span className="text-gray-400">~</span>
                      <label className="text-sm text-gray-600">終了日:</label>
                      <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="p-2 border rounded" />
                    </>
                  )}
                </div>

                {/* Public Absence Mode Selection */}
                {applicationType === "公欠" && (
                  <div className="flex gap-4 bg-gray-50 p-3 rounded">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="paMode" value="date" checked={publicAbsenceMode === "date"} onChange={() => setPublicAbsenceMode("date")} />
                      <span>日付指定 (全日)</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="paMode" value="period" checked={publicAbsenceMode === "period"} onChange={() => setPublicAbsenceMode("period")} />
                      <span>時限指定</span>
                    </label>
                  </div>
                )}

                {/* Class List */}
                {applicationType === "公欠" && publicAbsenceMode === "date" ? (
                  timetable.length > 0 ? (
                    <div className="p-4 bg-blue-50 text-blue-700 rounded-md border border-blue-200">
                      <p className="font-bold">対象期間の全ての授業（{timetable.length}コマ）が公欠として申請されます。</p>
                    </div>
                  ) : (
                    <p className="text-gray-500">授業がありません</p>
                  )
                ) : timetable.length > 0 ? (
                  <div className="space-y-2 mt-2">
                    {timetable.map((entry) => (
                      <label key={entry.id} className={`flex items-center gap-3 p-3 border rounded hover:bg-gray-50 cursor-pointer ${selectedClasses.includes(entry.id) ? "bg-blue-50 border-blue-200" : ""}`}>
                        <input type={applicationType === "早退" ? "radio" : "checkbox"} name={applicationType === "早退" ? "classSelection" : undefined} checked={selectedClasses.includes(entry.id)} onChange={() => handleClassSelection(entry.id)} className="w-5 h-5 text-blue-600 rounded" />
                        <div>
                          <span className="text-xs text-gray-500 block">{entry.date}</span>
                          <span className="font-bold mr-2">{entry.period}限</span>
                          <span className="mr-2">{entry.subject_name}</span>
                          <span className="text-sm text-gray-500">
                            ({entry.start_time} ~ {entry.end_time})
                          </span>
                        </div>
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">授業がありません</p>
                )}
              </div>
            </div>

            {/* 3. Reason */}
            <div className="mb-6">
              <h3 className="font-bold text-gray-700 mb-2">3. 理由</h3>

              {applicationType === "公欠" ? (
                <div className="space-y-3">
                  <select value={selectedReasonType} onChange={(e) => setSelectedReasonType(e.target.value)} className="w-full p-3 border rounded">
                    {PUBLIC_ABSENCE_REASONS.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>

                  {selectedReasonType === "その他" && <textarea className="w-full p-3 border rounded focus:ring-2 focus:ring-blue-500 outline-none" rows={3} placeholder="具体的な理由を入力してください" value={reason} onChange={(e) => setReason(e.target.value)} required></textarea>}
                </div>
              ) : (
                <textarea className="w-full p-3 border rounded focus:ring-2 focus:ring-blue-500 outline-none" rows={3} placeholder="具体的な理由を入力してください（例：体調不良のため、電車遅延のため）" value={reason} onChange={(e) => setReason(e.target.value)} required></textarea>
              )}
            </div>

            {appMessage && <div className={`mb-4 p-3 rounded ${appMessage.includes("完了") ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}`}>{appMessage}</div>}

            <button type="submit" className="w-full py-3 bg-blue-600 text-white font-bold rounded hover:bg-blue-700 transition-colors">
              申請する
            </button>
          </form>
        </section>
      </div>
    </main>
  );
}
