import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi, skillsApi, metaApi } from '../services/apiService'

type RecommendationCard = {
  title: string
  description: string
  tags: string[]
}

// 아이콘 SVG 컴포넌트
const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M21 21L15.0001 15.0001M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="#94A3B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const ProfilePage = () => {
  const [name, setName] = useState('홍길동')
  const [email, setEmail] = useState('hong@example.com')
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [scraps, setScraps] = useState<string[]>([])
  const [recentViews, setRecentViews] = useState<string[]>([])
  const navigate = useNavigate()
  const previewMode = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('preview') === 'true'

  // DB-driven career levels & experience ranges
  const [careerLevels, setCareerLevels] = useState<any[]>([])
  const [experienceRanges, setExperienceRanges] = useState<any[]>([])
  const [selectedCareerLevelId, setSelectedCareerLevelId] = useState<number | null>(null)
  const [selectedExperienceRangeId, setSelectedExperienceRangeId] = useState<number | null>(null)

  // DB-driven skills & wanted jobs (드롭다운 + 검색)
  const [allSkills, setAllSkills] = useState<string[]>([])
  const [loadingSkills, setLoadingSkills] = useState(true)
  const [selectedStacks, setSelectedStacks] = useState<string[]>([])
  const [isSkillSearchOpen, setIsSkillSearchOpen] = useState(false)
  const [skillSearchQuery, setSkillSearchQuery] = useState('')

  // 희망직무: DB의 DesiredJobs 예시 기반 기본값
  const [allWantedJobs, setAllWantedJobs] = useState<string[]>(['백엔드 개발자', '프론트엔드 개발자', '데이터 엔지니어'])
  const [loadingWantedJobs, setLoadingWantedJobs] = useState(false)
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [isJobSearchOpen, setIsJobSearchOpen] = useState(false)
  const [jobSearchQuery, setJobSearchQuery] = useState('')

  const [loadingMeta, setLoadingMeta] = useState(true)
  // 알림 항목: DB의 UserNotificationSettings 예시(채용 알림, 맞춤형 정보, 이벤트 소식)를 기반으로 표시
  type NotificationItem = { id: number; category: '채용 알림' | '맞춤형 정보' | '이벤트 소식'; text: string; timestamp: string }
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [isSaving, setIsSaving] = useState(false)

  // 프로필 저장 함수
  const handleSaveProfile = async () => {
    setIsSaving(true)
    try {
      const profileData = {
        name,
        email,
        careerLevelId: selectedCareerLevelId,
        experienceRangeId: selectedExperienceRangeId,
        skills: selectedStacks,
        wantedJobs: selectedInterests,
      }

      // 백엔드 API 호출 (예: PATCH /users/me)
      const response = await fetch('http://localhost:8000/users/me', {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
      })

      if (!response.ok) {
        throw new Error(`저장 실패: ${response.status}`)
      }

      // 성공 시에는 기존의 성공/오류 배너 대신 UI는 변경하지 않음
      // (알림에는 유저에게 유의미한 공고/정보/이벤트를 노출하도록 별도 로직이 필요)
    } catch (error) {
      console.error('Profile save error:', error)
      // 저장 실패 시에도 기존처럼 배너를 띄우지 않음 — 필요하면 별도 UI로 처리
    } finally {
      setIsSaving(false)
    }
  }

  // 알림(채용/정보/이벤트)을 히스토리에 추가
  const addNotificationToHistory = (category: NotificationItem['category'], text: string) => {
    const now = new Date()
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    setNotifications((prev) => [
      { id: Date.now(), category, text, timestamp },
      ...prev.slice(0, 9), // 최대 10개 유지
    ])
  }

  const toggleStack = (stack: string) => {
    setSelectedStacks((prev) =>
      prev.includes(stack) ? prev.filter((s) => s !== stack) : [...prev, stack]
    )
  }

  const toggleWantedJob = (job: string) => {
    setSelectedInterests((prev) =>
      prev.includes(job) ? prev.filter((j) => j !== job) : [...prev, job]
    )
  }

  // DB-driven skills 로드
  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const data = await skillsApi.getAllSkills()
        setAllSkills(data.skills || [])
      } catch (error) {
        console.error('Failed to fetch skills:', error)
        setAllSkills([])
      } finally {
        setLoadingSkills(false)
      }
    }
    fetchSkills()
  }, [])

  // DB-driven career levels & experience ranges 로드
  useEffect(() => {
    const fetchMeta = async () => {
      try {
        const [cls, ers] = await Promise.all([
          metaApi.getCareerLevels().catch((e) => {
            console.error(e)
            return []
          }),
          metaApi.getExperienceRanges().catch((e) => {
            console.error(e)
            return []
          }),
        ])

        const careerList = Array.isArray(cls) ? cls : cls?.careerlevels || []
        const expList = Array.isArray(ers) ? ers : ers?.experienceranges || []

        setCareerLevels(careerList)
        setExperienceRanges(expList)

        if (careerList.length > 0 && selectedCareerLevelId === null) {
          const firstId = careerList[0]?.id ?? careerList[0]?.CareerLevelID ?? null
          setSelectedCareerLevelId(firstId)
        }
        if (expList.length > 0 && selectedExperienceRangeId === null) {
          const firstId = expList[0]?.id ?? expList[0]?.RangeID ?? null
          setSelectedExperienceRangeId(firstId)
        }
      } finally {
        setLoadingMeta(false)
        setLoadingWantedJobs(false)
      }
    }
    fetchMeta()
  }, [])

  // 인증 확인: 로그인한 사용자만 접근 가능
  useEffect(() => {
    if (previewMode) {
      // 미리보기 모드: 인증 건너뜀, 샘플 데이터 세팅 (DB 예시 기준)
      setIsLoading(false)
      setScraps(['[샘플] Python 백엔드 채용 공고', '[샘플] 데이터 분석 인턴십'])
      setRecentViews(['[샘플] React 개발자 채용', '[샘플] ML 엔지니어 공고'])

      // Alembic 예시를 참고한 간단한 알림 샘플 (UserNotificationSettings 예시값 기반)
      setNotifications([
        { id: 1, category: '채용 알림', text: '[채용] Python 백엔드 개발자 - A회사', timestamp: '09:00' },
        { id: 2, category: '맞춤형 정보', text: '[정보] 당신에게 맞는 부트캠프가 업데이트되었습니다.', timestamp: '12:00' },
        { id: 3, category: '이벤트 소식', text: '[이벤트] 리액트 부트캠프 선착순 할인', timestamp: '18:00' },
      ])
      return
    }

    let mounted = true
    const check = async () => {
      try {
        const res = await authApi.getCurrentUser()
        if (!mounted) return
        if (!res || res.isLoggedIn !== true) {
          // 로그인 필요
          navigate('/login', { replace: true })
          return
        }

        // 사용자 정보 바인딩 (있으면 채워줌)
        const user = res.user || {}
        if (user.name) setName(user.name)
        if (user.email) setEmail(user.email)
        if (user.careerLevelId) setSelectedCareerLevelId(user.careerLevelId)
        if (user.experienceRangeId) setSelectedExperienceRangeId(user.experienceRangeId)
        if (Array.isArray(user.skills) && user.skills.length > 0) setSelectedStacks(user.skills)
        if (Array.isArray(user.wantedJobs) && user.wantedJobs.length > 0) setSelectedInterests(user.wantedJobs)
        if (Array.isArray(user.scraps)) setScraps(user.scraps)
        if (Array.isArray(user.recentViews)) setRecentViews(user.recentViews)
      } catch (e) {
        console.error('Profile: auth check failed', e)
        navigate('/login', { replace: true })
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    check()
    return () => {
      mounted = false
    }
  }, [navigate, previewMode])

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-semibold text-primary-700">내 프로필</p>
          <h1 className="text-3xl font-bold text-slate-950 sm:text-4xl">내 프로필</h1>
          <p className="text-base text-slate-600">프로필 정보를 확인하고 수정할 수 있습니다.</p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="text-lg font-bold text-slate-900">기본 정보</h2>
            <div className="mt-4 grid gap-4">
              {isLoading ? (
                <div className="text-sm text-slate-600">로그인 상태 확인 중...</div>
              ) : (
                <>
                  <label className="text-sm text-slate-700">
                    이름
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-100"
                      placeholder="이름을 입력하세요"
                    />
                  </label>

                  <label className="text-sm text-slate-700">
                    이메일
                    <input
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-100"
                      placeholder="이메일"
                    />
                  </label>
                </>
              )}

              <label className="text-sm text-slate-700">
                경력
                <div className="mt-2 grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-xs font-semibold text-slate-600">커리어 레벨</label>
                    <select
                      value={selectedCareerLevelId ?? ''}
                      onChange={(e) => setSelectedCareerLevelId(e.target.value ? Number(e.target.value) : null)}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-primary-600"
                    >
                      {careerLevels.length === 0 ? (
                        <option value="">불러오는 중...</option>
                      ) : (
                        careerLevels.map((c: any) => {
                          const id = c.id ?? c.CareerLevelID ?? c.careerlevelid
                          const name = c.name ?? c.CareerName ?? c.careername
                          return (
                            <option key={id} value={id}>
                              {name}
                            </option>
                          )
                        })
                      )}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-semibold text-slate-600">경력 구간</label>
                    <select
                      value={selectedExperienceRangeId ?? ''}
                      onChange={(e) => setSelectedExperienceRangeId(e.target.value ? Number(e.target.value) : null)}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-primary-600"
                    >
                      {experienceRanges.length === 0 ? (
                        <option value="">불러오는 중...</option>
                      ) : (
                        experienceRanges.map((r: any) => {
                          const id = r.id ?? r.RangeID ?? r.rangeid
                          const label = r.name ?? r.RangeName ?? r.rangename ?? r.label ?? r.range
                          return (
                            <option key={id} value={id}>
                              {label}
                            </option>
                          )
                        })
                      )}
                    </select>
                  </div>
                </div>
              </label>

              <div>
                <p className="text-sm font-semibold text-slate-900">희망직무</p>
                <div className="mt-3">
                  <div className="flex flex-wrap gap-2">
                    {selectedInterests.map((job) => (
                      <span
                        key={job}
                        className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700 ring-1 ring-inset ring-primary-200"
                      >
                        {job}
                        <button
                          onClick={() => toggleWantedJob(job)}
                          className="ml-2 text-primary-400 hover:text-primary-600"
                        >
                          ×
                        </button>
                      </span>
                    ))}

                    {/* + 선택 버튼 */}
                    <button
                      onClick={() => setIsJobSearchOpen(!isJobSearchOpen)}
                      className="flex items-center gap-1 rounded-full border border-dashed border-primary-300 bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700 transition hover:bg-primary-100"
                    >
                      + 직무 선택
                    </button>
                  </div>

                  {/* 검색창 UI 팝업 */}
                  {isJobSearchOpen && (
                    <div className="absolute left-0 mt-3 w-full z-10 px-6">
                      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xl ring-1 ring-slate-900/5">
                        {/* 검색 인풋 */}
                        <div className="relative mb-4">
                          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                            <SearchIcon />
                          </div>
                          <input
                            type="text"
                            value={jobSearchQuery}
                            onChange={(e) => setJobSearchQuery(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault()
                                const q = jobSearchQuery.trim()
                                if (!q) return

                                const found = allWantedJobs.find((j) => j.toLowerCase() === q.toLowerCase())
                                if (found) {
                                  toggleWantedJob(found)
                                } else {
                                  if (!selectedInterests.includes(q)) {
                                    setSelectedInterests((prev) => [...prev, q])
                                  }
                                }
                                setJobSearchQuery('')
                              }
                            }}
                            className="block w-full rounded-xl border-0 bg-white py-3 pl-10 pr-4 text-slate-900 ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                            placeholder="찾으시는 직무를 입력해주세요"
                            autoFocus
                          />
                        </div>

                        {/* 검색어가 목록에 없으면 직접 추가 버튼 */}
                        {jobSearchQuery.trim() !== '' &&
                          !allWantedJobs.some((j) => j.toLowerCase() === jobSearchQuery.trim().toLowerCase()) &&
                          !selectedInterests.includes(jobSearchQuery.trim()) && (
                            <div className="mb-2">
                              <button
                                onClick={() => {
                                  const q = jobSearchQuery.trim()
                                  if (!q) return
                                  setSelectedInterests((prev) => (prev.includes(q) ? prev : [...prev, q]))
                                  setJobSearchQuery('')
                                }}
                                className="rounded-full border px-4 py-2 text-sm transition-colors border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                              >
                                + 추가: "{jobSearchQuery}"
                              </button>
                            </div>
                          )}

                        {/* 직무 태그 목록 */}
                        <div className="flex max-h-48 flex-wrap gap-2 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
                          {loadingWantedJobs ? (
                            <div className="text-sm text-slate-500">불러오는 중...</div>
                          ) : (
                            allWantedJobs.map((job) => (
                              <button
                                key={job}
                                onClick={() => {
                                  toggleWantedJob(job)
                                  setJobSearchQuery('')
                                }}
                                className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                                  selectedInterests.includes(job)
                                    ? 'border-primary-200 bg-primary-50 text-primary-700 font-semibold'
                                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                                }`}
                              >
                                {job}
                              </button>
                            ))
                          )}
                        </div>
                      </div>
                      {/* 백드롭 (외부 클릭 시 닫기용) */}
                      <div
                        className="fixed inset-0 z-[-1]"
                        onClick={() => setIsJobSearchOpen(false)}
                      />
                    </div>
                  )}
                </div>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-900">기술스택</p>
                <div className="mt-3">
                  <div className="flex flex-wrap gap-2">
                    {selectedStacks.map((stack) => (
                      <span
                        key={stack}
                        className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-800 ring-1 ring-inset ring-slate-200"
                      >
                        {stack}
                        <button
                          onClick={() => toggleStack(stack)}
                          className="ml-2 text-slate-400 hover:text-slate-600"
                        >
                          ×
                        </button>
                      </span>
                    ))}

                    {/* + 선택 버튼 */}
                    <button
                      onClick={() => setIsSkillSearchOpen(!isSkillSearchOpen)}
                      className="flex items-center gap-1 rounded-full border border-dashed border-primary-300 bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700 transition hover:bg-primary-100"
                    >
                      + 스킬 선택
                    </button>
                  </div>

                  {/* 검색창 UI 팝업 */}
                  {isSkillSearchOpen && (
                    <div className="absolute left-0 mt-3 w-full z-10 px-6">
                      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xl ring-1 ring-slate-900/5">
                        {/* 검색 인풋 */}
                        <div className="relative mb-4">
                          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                            <SearchIcon />
                          </div>
                          <input
                            type="text"
                            value={skillSearchQuery}
                            onChange={(e) => setSkillSearchQuery(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault()
                                const q = skillSearchQuery.trim()
                                if (!q) return

                                const found = allSkills.find((s) => s.toLowerCase() === q.toLowerCase())
                                if (found) {
                                  toggleStack(found)
                                } else {
                                  if (!selectedStacks.includes(q)) {
                                    setSelectedStacks((prev) => [...prev, q])
                                  }
                                }
                                setSkillSearchQuery('')
                              }
                            }}
                            className="block w-full rounded-xl border-0 bg-white py-3 pl-10 pr-4 text-slate-900 ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                            placeholder="찾으시는 스킬을 입력해주세요"
                            autoFocus
                          />
                        </div>

                        {/* 검색어가 목록에 없으면 직접 추가 버튼 */}
                        {skillSearchQuery.trim() !== '' &&
                          !allSkills.some((s) => s.toLowerCase() === skillSearchQuery.trim().toLowerCase()) &&
                          !selectedStacks.includes(skillSearchQuery.trim()) && (
                            <div className="mb-2">
                              <button
                                onClick={() => {
                                  const q = skillSearchQuery.trim()
                                  if (!q) return
                                  setSelectedStacks((prev) => (prev.includes(q) ? prev : [...prev, q]))
                                  setSkillSearchQuery('')
                                }}
                                className="rounded-full border px-4 py-2 text-sm transition-colors border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                              >
                                + 추가: "{skillSearchQuery}"
                              </button>
                            </div>
                          )}

                        {/* 스킬 태그 목록 */}
                        <div className="flex max-h-48 flex-wrap gap-2 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
                          {loadingSkills ? (
                            <div className="text-sm text-slate-500">불러오는 중...</div>
                          ) : (
                            allSkills.map((skill) => (
                              <button
                                key={skill}
                                onClick={() => {
                                  toggleStack(skill)
                                  setSkillSearchQuery('')
                                }}
                                className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                                  selectedStacks.includes(skill)
                                    ? 'border-primary-200 bg-primary-50 text-primary-700 font-semibold'
                                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                                }`}
                              >
                                {skill}
                              </button>
                            ))
                          )}
                        </div>
                      </div>
                      {/* 백드롭 (외부 클릭 시 닫기용) */}
                      <div
                        className="fixed inset-0 z-[-1]"
                        onClick={() => setIsSkillSearchOpen(false)}
                      />
                    </div>
                  )}
                </div>
              </div>

              <button
                onClick={handleSaveProfile}
                disabled={isSaving}
                className="mt-2 w-full rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 px-4 py-3 text-sm font-semibold text-white shadow-soft transition hover:shadow-lg hover:shadow-primary-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? '저장 중...' : '저장'}
              </button>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-100 bg-slate-50/70 p-6 shadow-soft">
            {/* 알림 영역: 채용 알림 / 맞춤형 정보 / 이벤트 소식 - 스크랩/최근열람과 동일한 카드 형식으로 노출 */}
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">알림 이력</h3>
                {notifications.length === 0 ? (
                  <div className="mt-2 rounded-xl border border-dashed border-slate-200 bg-white p-3 text-sm text-slate-600">알림 이력이 없습니다.</div>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {notifications.map((notif) => (
                      <li key={notif.id} className="rounded-md border border-slate-100 bg-white p-3 text-sm text-slate-800">
                        <div className="flex items-start justify-between">
                          <span className="font-medium">[{notif.category}] {notif.text}</span>
                          <span className="text-xs opacity-70">{notif.timestamp}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900">스크랩</h3>
                {scraps.length === 0 ? (
                  <div className="mt-2 rounded-xl border border-dashed border-slate-200 bg-white p-3 text-sm text-slate-600">스크랩한 공고가 없습니다.</div>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {scraps.map((s, i) => (
                      <li key={i} className="rounded-md border border-slate-100 bg-white p-3 text-sm text-slate-800">{s}</li>
                    ))}
                  </ul>
                )}
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900">최근 열람 공고</h3>
                {recentViews.length === 0 ? (
                  <div className="mt-2 rounded-xl border border-dashed border-slate-200 bg-white p-3 text-sm text-slate-600">최근 열람한 공고가 없습니다.</div>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {recentViews.map((r, i) => (
                      <li key={i} className="rounded-md border border-slate-100 bg-white p-3 text-sm text-slate-800">{r}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
