import { useAuth } from "../../api/useAuth";

export default function AdminHeader() {
  const { user } = useAuth();
  console.log("ADMIN HEADER USER:", user);

  return (
    <header className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <h2 className="text-xl font-semibold">관리자 페이지</h2>

      <div className="flex items-center gap-4">
        <span className="font-medium text-gray-700">{user?.name} (Admin)</span>
      </div>
    </header>
  );
}