"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

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

const todayweekDayNames = ["日", "月", "火", "水", "木", "金", "土"];
const todayDate = new Date();
const month = todayDate.getMonth() + 1;
const day = todayDate.getDate();
const weekDay = todayweekDayNames[todayDate.getDay()];





  const today = formatDate(new Date());
  const todayTimetable = timetable
    .filter((t) => t.date === today)
    .sort((a, b) => a.period - b.period);


  useEffect(() => {
    const fetchMajors = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const res = await fetch("/api/timetables/majors", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          setMajors(data.majors);
        }
      } catch (error) {
        console.error("Failed to fetch majors", error);
      }
    };

    fetchMajors();
  }, []);

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
  <div className="rounded-lg border bg-white shadow-sm">
    {/* タイトル & 日付 */}
    <div className="border-b p-4">
      <h2 className="text-lg font-semibold">今日の時間割</h2>
      <p className="mt-1 text-sm text-gray-600">
        {month}月{day}日（{weekDay}）
      </p>
    </div>

    {/* 時間割 */}
    <div className="p-4">
      {loading ? (
        <p className="text-sm text-gray-500">読み込み中...</p>
      ) : todayTimetable.length === 0 ? (
        <p className="text-sm text-gray-500">今日の授業はありません</p>
      ) : (
        <div className="overflow-hidden rounded-md border">
          <div className="grid grid-cols-[55px_1fr] bg-gray-50 text-sm font-medium">
            <div className="border-r px-3 py-2">時限</div>
            <div className="px-3 py-2">科目</div>
          </div>

          {todayTimetable.map((t) => (
            <div
              key={t.id}
              className="grid grid-cols-[55px_1fr] border-t text-sm"
            >
              <div className="border-r px-3 py-2 text-gray-700">
                {t.period}限
              </div>
              <div className="px-3 py-2 text-gray-900">
                {t.subject_name}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);
}