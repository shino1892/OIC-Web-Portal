"use client";
import TimeTable from "./Timetable";
import AttendanceSummary from "./Attendance";

type Props = {
  name: string;
};

export default function App({ name }: Props) {
return (
<div className="mx-auto max-w-6xl px-4">
  <div className="grid gap-6 md:grid-cols-2">
    <TimeTable />
    <AttendanceSummary />
  </div>
</div>
);
}
