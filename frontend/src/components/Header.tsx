import { useEffect, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

type NavItem = {
  label: string
  to: string
}

const navItems: NavItem[] = [
  { label: '홈', to: '/' },
  { label: '채용', to: '/jobs' },
  { label: '부트캠프', to: '/bootcamps' },
  { label: '프로필', to: '/profile' },
]

// Cookie helper used to check login state
const getCookie = (name: string): string | null => {
  if (typeof document === 'undefined') return null
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() ?? null
  return null
}

const Header = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    const checkLoginStatus = () => {
      const isLoggedInLocal = localStorage.getItem('isLoggedIn') === 'true'
      const token = getCookie('kakao_access_token')
      setIsLoggedIn(isLoggedInLocal || !!token)
    }

    checkLoginStatus()
    const interval = setInterval(checkLoginStatus, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('userName')
    localStorage.removeItem('userEmail')
    document.cookie = 'kakao_access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'kakao_refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    setIsLoggedIn(false)
  }

  return (
    <header className="sticky top-0 z-30 border-b border-slate-100 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 text-base font-bold text-white shadow-soft">
            IT
          </span>
          <div className="leading-tight">
            <p className="text-sm font-semibold text-primary-700">MatchIT</p>
            <p className="text-xs text-slate-500">맞춤 채용 · 부트캠프 추천</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium text-slate-700 md:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  'transition-colors hover:text-primary-600',
                  isActive ? 'text-primary-600' : 'text-slate-700',
                ].join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {isLoggedIn ? (
            <button
              onClick={handleLogout}
              className="hidden rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-red-200 hover:text-red-600 md:inline-flex"
            >
              로그아웃
            </button>
          ) : (
            <Link
              to="/login"
              className="hidden rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-primary-200 hover:text-primary-700 md:inline-flex"
            >
              로그인
            </Link>
          )}
          <Link
            to="/"
            className="rounded-full bg-gradient-to-r from-primary-500 to-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:shadow-lg hover:shadow-primary-200"
          >
            추천 받기
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header
