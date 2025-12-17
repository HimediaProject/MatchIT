import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'

import googleIcon from "../images/google.png";
import kakaoIcon from "../images/kakao.png";
import naverIcon from "../images/naver.png";

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const checkExecuted = useRef(false)

  // 로그인 페이지 진입 시 캐시 상태 확인 및 정리 (한 번만 실행)
  useEffect(() => {
    if (checkExecuted.current) return
    checkExecuted.current = true

    const cleanupAuthCache = async () => {
      try {
        console.log('[LoginPage] 로그인 페이지 진입, 캐시 상태 확인 중...')
        
        // 현재 로그인 상태 확인
        const result = await authApi.getCurrentUser()
        console.log('[LoginPage] 현재 로그인 상태:', result)
        
        if (result?.isLoggedIn === true) {
          // 이미 로그인된 상태면 홈으로 리다이렉트
          console.log('[LoginPage] 이미 로그인됨, 홈으로 이동')
          navigate('/', { replace: true })
        }
      } catch (e) {
        console.error('[LoginPage] 캐시 확인 중 오류:', e)
      }
    }

    // 약간의 딜레이 후 실행
    const timer = setTimeout(() => {
      cleanupAuthCache()
    }, 100)

    return () => clearTimeout(timer)
  }, [navigate])

  const handleSocialLogin = async (provider: string) => {
    try {
      setIsLoading(true)
      // 외부 인증 페이지로 이동
      window.location.href = authApi.getSocialLoginUrl(provider)
    } catch (e) {
      console.error(e)
      alert('소셜 로그인 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(45,109,255,0.04),transparent_30%),radial-gradient(circle_at_80%_10%,rgba(245,159,0,0.04),transparent_20%)]" />
        <div className="relative mx-auto grid max-w-4xl grid-cols-1 items-center gap-10 px-4 py-20 md:px-6 lg:grid-cols-2">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-4 py-2 text-sm font-semibold text-primary-700">
              간편 로그인
            </div>
            <div className="space-y-4">
              <h1 className="text-3xl font-bold leading-tight text-slate-950 sm:text-4xl lg:text-4xl">
                MatchIT에 로그인하여
                <br /> 나만의 추천을 받아보세요.
              </h1>
              <p className="max-w-md text-lg text-slate-600">
                소셜 계정으로 간편하게 로그인하면 프로필을 저장하고 맞춤 추천을 계속 받을 수 있습니다.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => navigate('/')}
                className="rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-800 transition hover:border-primary-200 hover:text-primary-700"
              >
                뒤로가기
              </button>
            </div>
          </div>

          <div className="relative">
            <div className="relative rounded-3xl border border-slate-100 bg-white/90 p-8 shadow-soft">
              <div className="text-center mb-6">
                <div className="w-20 h-20 mx-auto mb-4 flex items-center justify-center rounded-xl bg-primary-50 text-primary-700 text-2xl font-bold">IT</div>
                <h3 className="text-lg font-bold text-slate-900">소셜 계정으로 로그인</h3>
                <p className="text-sm text-slate-500">Google / Kakao / Naver 계정으로 빠르게 시작하세요.</p>
              </div>

              <div className="space-y-3">
                <button
                  disabled={isLoading}
                  onClick={() => handleSocialLogin('google')}
                  className="w-full py-3 px-4
                             border border-slate-200
                             bg-white hover:bg-slate-50
                             flex items-center gap-4
                             rounded-xl
                             transition
                             hover:shadow-sm
                             disabled:opacity-50"
                >
                  <div className="w-8 h-8 flex items-center justify-center">
                    <img
                      src={googleIcon}
                      alt="구글 로그인"
                      className="w-8 h-8 object-contain cursor-pointer"
                    ></img>
                  </div>
                  <span className="flex-1 text-left">Google 계정으로 로그인</span>
                </button>

                <button
                  disabled={isLoading}
                  onClick={() => handleSocialLogin('kakao')}
                  className="w-full py-3 px-4
                             border border-slate-200
                             bg-white hover:bg-slate-50
                             flex items-center gap-4
                             rounded-xl
                             transition
                             hover:shadow-sm
                             disabled:opacity-50"
                >
                  <div className="w-8 h-8 flex items-center justify-center">
                    <img
                      src={kakaoIcon}
                      alt="카카오 로그인"
                      className="w-7 h-7 object-contain cursor-pointer"
                    ></img>
                  </div>
                  <span className="flex-1 text-left">Kakao 계정으로 로그인</span>
                </button>

                <button
                  disabled={isLoading}
                  onClick={() => handleSocialLogin('naver')}
                  className="w-full py-3 px-4
                             border border-slate-200
                             bg-white hover:bg-slate-50
                             flex items-center gap-4
                             rounded-xl
                             transition
                             hover:shadow-sm
                             disabled:opacity-50"
                >
                  <div className="w-8 h-8 flex items-center justify-center">
                    <img
                      src={naverIcon}
                      alt="네이버 로그인"
                      className="w-8 h-8 object-contain cursor-pointer"
                    ></img>
                  </div>
                  <span className="flex-1 text-left">Naver 계정으로 로그인</span>
                </button>
              </div>

              <div className="mt-6 text-center">
                <p className="text-xs text-slate-500 mb-3">로그인 시 약관에 동의하게 됩니다.</p>
                <div className="flex gap-2 justify-center text-xs">
                  <button className="underline">이용약관</button>
                  <span>|</span>
                  <button className="underline">개인정보처리방침</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}