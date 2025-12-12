import { Link, useLocation } from "react-router-dom";

export default function AdminSidebar() {
  const { pathname } = useLocation();

  const menu = [
    { to: "/admin", label: "📊 대시보드" },
    { to: "/admin/users", label: "👥 회원 관리" },
    { to: "/admin/jobposts", label: "💼 채용 공고 관리" },
    { to: "/admin/bootcamps", label: "🎓 부트캠프 관리" }
  ];

  return (
    <aside className="w-64 bg-white shadow-md p-6 border-r border-gray-200">
      <Link to="/" className="flex items-center gap-2 mb-8">
        <span className="text-2xl font-bold text-primary-600">MatchIT</span>
        <span className="text-xs text-amber-600 font-semibold">Admin</span>
      </Link>

      <nav className="space-y-2">
        {menu.map((m) => (
          <Link
            key={m.to}
            to={m.to}
            className={`block px-4 py-3 rounded-lg font-medium transition ${
              pathname === m.to
                ? "bg-primary-50 text-primary-700 border-l-4 border-primary-600"
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            {m.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
