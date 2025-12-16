import { useAuth } from "../../api/useAuth";

export default function AdminHeader() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <h2 className="text-xl font-semibold">관리자 페이지</h2>

      <div className="flex items-center gap-4">
        <span className="font-medium text-gray-700">{user?.name} (Admin)</span>

        <button
          onClick={logout}
          className="px-4 py-1 bg-red-500 rounded-md text-white"
        >
          로그아웃
        </button>
      </div>
    </header>
  );
}