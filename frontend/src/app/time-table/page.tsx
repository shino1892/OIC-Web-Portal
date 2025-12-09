"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AttendanceModal from "@/components/AttendanceModal";

interface TimetableEntry {
  id: number;
  date: string;
  period: number;
  subject_name: string;
  teacher_name: string;
  major_id: number | null;
}

interface Major {
  id: number;
  name: string;
}

export default function TimeTable() {
  const router = useRouter();
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [selectedMajor, setSelectedMajor] = useState<number | null>(null);
  const [majors, setMajors] = useState<Major[]>([]);
  const [userId, setUserId] = useState<number | null>(null);
  const [selectedClass, setSelectedClass] = useState<TimetableEntry | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Helper to get Monday of the current week
  const getMonday = (d: Date) => {
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // adjust when day is sunday
    const monday = new Date(d);
    monday.setDate(diff);
    return monday;
  };

  const startOfWeek = getMonday(new Date(currentDate));
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);

  // Display end date (Friday)
  const displayEndOfWeek = new Date(startOfWeek);
  displayEndOfWeek.setDate(startOfWeek.getDate() + 4);

  const formatDate = (d: Date) => {
    const year = d.getFullYear();
    const month = ("0" + (d.getMonth() + 1)).slice(-2);
    const day = ("0" + d.getDate()).slice(-2);
    return `${year}-${month}-${day}`;
  };

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        // 1. Fetch User Info to get default major and userId
        let defaultMajorId: number | null = null;
        const userRes = await fetch("/api/users/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (userRes.ok) {
          const userData = await userRes.json();
          setUserId(userData.user_id);
          if (userData.major_id) {
            defaultMajorId = userData.major_id;
          }
        }

        // 2. Fetch Majors
        const majorsRes = await fetch("/api/timetables/majors", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (majorsRes.ok) {
          const data = await majorsRes.json();
          setMajors(data.majors);

          // Set default selection
          if (defaultMajorId) {
            setSelectedMajor(defaultMajorId);
          } else if (data.majors.length > 0) {
            // If user has no major but majors exist, select the first one
            setSelectedMajor(data.majors[0].id);
          }
        }
      } catch (error) {
        console.error("Failed to fetch initial data", error);
      }
    };

    init();
  }, []);

  const handleClassClick = (entry: TimetableEntry) => {
    setSelectedClass(entry);
    setIsModalOpen(true);
  };

  useEffect(() => {
    const fetchTimetable = async () => {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      const start = formatDate(startOfWeek);
      const end = formatDate(endOfWeek);

      let url = `/api/timetables/?start_date=${start}&end_date=${end}`;
      if (selectedMajor) {
        url += `&major_id=${selectedMajor}`;
      }

      try {
        const res = await fetch(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setTimetable(data);
        } else {
          if (res.status === 401) {
            router.push("/login");
          }
          console.error("Failed to fetch timetable");
        }
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchTimetable();
  }, [currentDate, selectedMajor]); // eslint-disable-line react-hooks/exhaustive-deps

  const handlePrevWeek = () => {
    const newDate = new Date(currentDate);
    newDate.setDate(newDate.getDate() - 7);
    setCurrentDate(newDate);
  };

  const handleNextWeek = () => {
    const newDate = new Date(currentDate);
    newDate.setDate(newDate.getDate() + 7);
    setCurrentDate(newDate);
  };

  // Grid rendering logic
  const periods = [1, 2, 3, 4, 5, 6, 7];
  const weekDays = [0, 1, 2, 3, 4]; // Mon-Fri (offset from startOfWeek)
  const weekDayNames = ["月", "火", "水", "木", "金"];

  const getEntry = (dayOffset: number, period: number) => {
    const targetDate = new Date(startOfWeek);
    targetDate.setDate(targetDate.getDate() + dayOffset);
    const dateStr = formatDate(targetDate);

    return timetable.find((t) => t.date === dateStr && t.period === period);
  };

  return (
    <main className="p-4 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-800">時間割</h1>

        <div className="flex items-center gap-4">
          {majors.length > 0 && (
            <select value={selectedMajor || ""} onChange={(e) => setSelectedMajor(Number(e.target.value))} className="p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {majors.map((major) => (
                <option key={major.id} value={major.id}>
                  {major.name}
                </option>
              ))}
            </select>
          )}

          <div className="flex items-center gap-4 bg-white p-2 rounded-lg shadow-sm">
            <button onClick={handlePrevWeek} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors">
              &lt; 先週
            </button>
            <span className="font-bold text-lg min-w-[200px] text-center">
              {formatDate(startOfWeek)} 〜 {formatDate(displayEndOfWeek)}
            </span>
            <button onClick={handleNextWeek} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors">
              来週 &gt;
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="overflow-x-auto bg-white rounded-lg shadow">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="border-b border-r border-gray-200 p-3 bg-gray-50 w-16 text-gray-600">時限</th>
                {weekDayNames.map((name, index) => {
                  const d = new Date(startOfWeek);
                  d.setDate(d.getDate() + index);
                  const isToday = formatDate(d) === formatDate(new Date());
                  return (
                    <th key={index} className={`border-b border-r border-gray-200 p-3 min-w-[150px] ${isToday ? "bg-blue-50" : "bg-gray-50"}`}>
                      <div className="flex flex-col items-center">
                        <span className="font-bold text-gray-800">{name}</span>
                        <span className="text-xs text-gray-500 font-normal">
                          {d.getMonth() + 1}/{d.getDate()}
                        </span>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {periods.map((period) => (
                <tr key={period}>
                  <td className="border-b border-r border-gray-200 p-3 text-center font-bold bg-gray-50 text-gray-600">{period}</td>
                  {weekDays.map((dayOffset) => {
                    const entry = getEntry(dayOffset, period);
                    const d = new Date(startOfWeek);
                    d.setDate(d.getDate() + dayOffset);
                    const isToday = formatDate(d) === formatDate(new Date());

                    return (
                      <td key={dayOffset} className={`border-b border-r border-gray-200 p-2 h-24 align-top transition-colors hover:bg-gray-50 ${isToday ? "bg-blue-50/30" : ""}`}>
                        {entry ? (
                          <div onClick={() => handleClassClick(entry)} className="flex flex-col h-full justify-between p-1 rounded hover:bg-white hover:shadow-sm transition-all cursor-pointer">
                            <span className="font-bold text-sm text-gray-800 line-clamp-2">{entry.subject_name}</span>
                            <div className="mt-2 flex justify-end">
                              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{entry.teacher_name}</span>
                            </div>
                          </div>
                        ) : (
                          <div className="h-full flex items-center justify-center">
                            <span className="text-gray-200 text-2xl font-light">-</span>
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedClass && userId && (
        <AttendanceModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          timetableId={selectedClass.id}
          userId={userId}
          subjectName={selectedClass.subject_name}
          onSuccess={(msg) => {
            // Optional: Refresh data or show toast
            console.log(msg);
          }}
        />
      )}
    </main>
  );
}
