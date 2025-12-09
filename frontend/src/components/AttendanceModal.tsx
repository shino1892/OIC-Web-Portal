import React, { useState } from "react";

interface AttendanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  timetableId: number;
  userId: number;
  subjectName: string;
  onSuccess: (message: string) => void;
}

export default function AttendanceModal({ isOpen, onClose, timetableId, userId, subjectName, onSuccess }: AttendanceModalProps) {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleAttend = async () => {
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/attendance/attend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ user_id: userId, timetable_id: timetableId }),
      });

      const data = await res.json();
      if (res.ok) {
        setMessage(data.message);
        if (data.status) {
          setMessage(`出席登録完了: ${data.status}`);
        }
        setTimeout(() => {
          onSuccess(data.message);
          onClose();
        }, 1500);
      } else {
        setError(data.message);
      }
    } catch (e) {
      setError("通信エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (status: string) => {
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/attendance/status", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ user_id: userId, timetable_id: timetableId, status }),
      });

      const data = await res.json();
      if (res.ok) {
        setMessage(`${status}申請が完了しました`);
        setTimeout(() => {
          onSuccess(`${status}申請が完了しました`);
          onClose();
        }, 1500);
      } else {
        setError(data.message);
      }
    } catch (e) {
      setError("通信エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
        <h2 className="text-xl font-bold mb-4">{subjectName}</h2>

        {message && <div className="mb-4 p-2 bg-green-100 text-green-700 rounded">{message}</div>}
        {error && <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">{error}</div>}

        <div className="flex flex-col gap-3">
          <button onClick={handleAttend} disabled={loading} className="w-full py-3 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-400">
            {loading ? "処理中..." : "出席する"}
          </button>
        </div>

        <button onClick={onClose} className="mt-6 text-gray-500 hover:text-gray-700 w-full text-center">
          閉じる
        </button>
      </div>
    </div>
  );
}
