"use client";
import { useState } from "react";

interface Major {
  id: number;
  name: string;
}

interface Props {
  majors: Major[];
  onSelect: (majorId: number) => void;
}

export default function MajorSelectionModal({ majors, onSelect }: Props) {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const handleSubmit = () => {
    if (selectedId) {
      onSelect(selectedId);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
        <h2 className="text-xl font-bold mb-4">専攻の選択</h2>
        <p className="mb-4 text-gray-600">所属する専攻を選択してください。</p>

        <div className="space-y-2 mb-6">
          {majors.map((major) => (
            <label key={major.id} className="flex items-center gap-3 p-3 border rounded hover:bg-gray-50 cursor-pointer">
              <input type="radio" name="major" value={major.id} checked={selectedId === major.id} onChange={() => setSelectedId(major.id)} className="w-5 h-5 text-blue-600" />
              <span>{major.name}</span>
            </label>
          ))}
        </div>

        <button onClick={handleSubmit} disabled={!selectedId} className="w-full py-2 bg-blue-600 text-white font-bold rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed">
          決定
        </button>
      </div>
    </div>
  );
}
