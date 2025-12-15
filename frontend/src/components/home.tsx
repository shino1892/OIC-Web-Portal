"use client";
import TimeTable from "./Timetable";

type Props = {
  name: string;
};

export default function App({ name }: Props) {
  return (
    <div>
      <h1>Hello {name}!</h1>

      <TimeTable />
    </div>
  );
}