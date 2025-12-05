import { useEffect, useState, useCallback } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { authApi } from '../services/apiService'

type NavItem = {
  label: string
  to: string
}

const navItems: NavItem[] = [
  { label: '홈', to: '/' },
  { label: '채용', to: '/jobs' },
  { label: '부트캠프', to: '/bootcamps' },
  { label: '내 프로필', to: '/profile' },
]

const Header = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const navigate = useNavigate()

  // API를 통해 로그인 상태 확인
  const checkLoginStatus = useCallback(async () => {
    try {
      const result = await authApi.getCurrentUser()
      console.log('Login status from API:', result)
      setIsLoggedIn(result.isLoggedIn === true)
    } catch (error) {
      console.error('Error checking login status:', error)
      setIsLoggedIn(false)
    }
  }, [])

  // 마운트 시 + 정기적으로 확인
  useEffect(() => {
    checkLoginStatus()

    // 1초마다 확인 (빠른 반응성)
    const interval = setInterval(checkLoginStatus, 1000)

    return () => {
      clearInterval(interval)
    }
  }, [checkLoginStatus])

  const handleLogout = async () => {
    try {
      console.log('[LOGOUT] 로그아웃 시작...')
      
      // 1. 로컬스토리지에서 모든 사용자 데이터 삭제
      const cacheKeys = [
        'isLogin',
        'isLoggedIn',
        'isNewUser',
        'access_token',
        'userName',
        'userEmail',
        'kakao_access_token',
        'naver_access_token',
        'google_access_token',
      ]
      
      cacheKeys.forEach(key => {
        try {
          localStorage.removeItem(key)
          sessionStorage.removeItem(key)
          console.log(`[LOGOUT] 캐시 삭제: ${key}`)
        } catch (e) {
          console.warn(`캐시 항목 삭제 실패: ${key}`, e)
        }
      })

      // 2. IndexedDB 캐시 삭제
      try {
        const dbs = await window.indexedDB.databases?.()
        if (dbs) {
          dbs.forEach(db => {
            if (db.name) {
              indexedDB.deleteDatabase(db.name)
              console.log(`[LOGOUT] IndexedDB 삭제: ${db.name}`)
            }
          })
        }
      } catch (e) {
        console.warn('IndexedDB 삭제 중 오류:', e)
      }

      // 3. 모든 쿠키 삭제 (document.cookie 사용)
      const cookieNames = ['session_id', 'user_id', 'is_login']
      cookieNames.forEach(name => {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
        document.cookie = `${name}=; max-age=0; path=/;`
        console.log(`[LOGOUT] 쿠키 삭제: ${name}`)
      })

      // 4. AJAX로 로그아웃 요청을 보내면 서버가 쿠키를 삭제하고 JSON을 반환합니다.
      const resp = await fetch('http://localhost:8000/auth/kakao/logout', {
        method: 'GET',
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      })

      console.log('[LOGOUT] 서버 응답:', resp.status)

      // 5. 상태 업데이트 및 페이지 리로드
      setIsLoggedIn(false)
      
      // 페이지 완전 새로고침으로 모든 상태 초기화
      setTimeout(() => {
        console.log('[LOGOUT] 페이지 리로드')
        window.location.href = '/'
      }, 300)
    } catch (error) {
      console.error('[LOGOUT] 로그아웃 중 오류:', error)
      // 네트워크 에러 등인 경우에도 페이지 새로고침
      setTimeout(() => {
        window.location.href = '/'
      }, 200)
    }
  }

  return (
    <header className="sticky top-0 z-30 border-b border-slate-100 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 text-base font-bold text-white shadow-soft">
            IT
          </span>
          <div className="leading-tight">
            <p className="text-sm font-semibold text-primary-700">MatchIt</p>
            <p className="text-xs text-slate-500">맞춤 채용/부트캠프 추천</p>
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
            지금 바로 추천 받기
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header