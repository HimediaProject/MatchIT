import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { skillsApi } from '../api/skills'
import { metaApi } from '../api/meta'
import { usersApi } from '../api/users'

// 아이콘 SVG 컴포넌트
const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M21 21L15.0001 15.0001M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="#94A3B8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const ProfilePage = () => {
  const [name, setName] = useState('홍길동')
  const [email, setEmail] = useState('hong@example.com')
  const [isLoading, setIsLoading] = useState(true)
  type ScrapItem = { postType: 'Job' | 'Bootcamp'; targetId: number; label: string }
  type RecentViewItem = { postType?: 'Job' | 'Bootcamp'; targetId?: number; label: string }

  const [scraps, setScraps] = useState<ScrapItem[]>([])
  const [recentviews, setRecentViews] = useState<RecentViewItem[]>([])
  const navigate = useNavigate()
  const previewMode = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('preview') === 'true'

  // DB-driven career levels & experience ranges
  const [careerLevels, setCareerLevels] = useState<any[]>([])
  const [experienceRanges, setExperienceRanges] = useState<any[]>([])
  const [selectedCareerLevelId, setSelectedCareerLevelId] = useState<number | null>(null)
  const [selectedExperienceRangeId, setSelectedExperienceRangeId] = useState<number | null>(null)
  const [fetchedCareerName, setFetchedCareerName] = useState<string | null>(null)
  const [fetchedExperienceName, setFetchedExperienceName] = useState<string | null>(null)

  // DB-driven skills & wanted jobs (드롭다운 + 검색)
  const [allSkills, setAllSkills] = useState<string[]>([])
  const [loadingSkills, setLoadingSkills] = useState(true)
  const [selectedStacks, setSelectedStacks] = useState<string[]>([])
  const [isSkillSearchOpen, setIsSkillSearchOpen] = useState(false)
  const [skillSearchQuery, setSkillSearchQuery] = useState('')

  // 희망직무: DB의 DesiredJobs에서 동적으로 로드
  const [allWantedJobs, setAllWantedJobs] = useState<string[]>([])
  const [loadingWantedJobs, setLoadingWantedJobs] = useState(true)
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [isJobSearchOpen, setIsJobSearchOpen] = useState(false)
  const [jobSearchQuery, setJobSearchQuery] = useState('')

  const [loadingMeta, setLoadingMeta] = useState(true)
  // 알림 항목: DB의 UserNotificationSettings 예시(채용 알림, 맞춤형 정보, 이벤트 소식)를 기반으로 표시
  type NotificationItem = { id: number; category: '채용 알림' | '맞춤형 정보' | '이벤트 소식'; text: string; timestamp: string }
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [isSaving, setIsSaving] = useState(false)

  // 스크랩 삭제 핸들러
  const handleDeleteScrap = async (index: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return

    const target = scraps[index]
    if (!target) return

    try {
      await usersApi.removeMyScrap(target.postType, target.targetId)
    } catch (e) {
      console.error('스크랩 삭제 실패:', e)
      alert('스크랩 삭제에 실패했습니다.')
      return
    }

    const newScraps = [...scraps]
    newScraps.splice(index, 1)
    setScraps(newScraps)
  }

  // 최근 열람 삭제 핸들러
  const handleDeleteRecentView = (index: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return

    const newRecentViews = [...recentViews]
    newRecentViews.splice(index, 1)
    setRecentViews(newRecentViews)
    localStorage.setItem('recentviews', JSON.stringify(newRecentViews))
  }

  // 프로필 저장 함수
  const handleSaveProfile = async () => {
    setIsSaving(true)
    try {
      // 최근 열람 공고를 저장 전에 읽기
      let recentviewsToSave: string[] = []
      try {
        const raw = localStorage.getItem('recentviews')
        if (raw) {
          const parsed = JSON.parse(raw)
          if (Array.isArray(parsed)) {
            recentviewsToSave = parsed
              .map((x: any) => {
                if (typeof x === 'string') return String(x)
                if (x && typeof x === 'object') return String(x.label ?? x.title ?? '')
                return ''
              })
              .filter(Boolean)
              .slice(0, 5)
          }
        }
      } catch (e) {
        // ignore
      }

      const profileData = {
        name,
        email,
        career_level: selectedCareerLevelId,
        experience_range: selectedExperienceRangeId,
        skills: selectedStacks,
        desired_jobs: selectedInterests,
        recentviews: recentviewsToSave,
      }

      console.log('프로필 저장 요청:', profileData)
      const result = await usersApi.updateMyProfile(profileData)
      console.log('프로필 저장 완료:', result)
      alert('프로필이 저장되었습니다.')
    } catch (error) {
      console.error('Profile save error:', error)
      alert('프로필 저장에 실패했습니다: ' + String(error))
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
      ...prev.slice(0, 2), // 최대 3개 유지
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

  // 메타(커리어 레벨)가 로드된 이후에, 서버에서 받은 career name을 ID로 매핑
  useEffect(() => {
    if (fetchedCareerName && careerLevels.length > 0) {
      const careerLevel = careerLevels.find((c: any) => {
        const name = c.name || c.CareerName || c.careername
        return name === fetchedCareerName
      })
      if (careerLevel) {
        const id = careerLevel.id || careerLevel.CareerLevelID || careerLevel.careerlevelid
        setSelectedCareerLevelId(id)
      }
      setFetchedCareerName(null)
    }
  }, [careerLevels, fetchedCareerName])

  useEffect(() => {
    if (fetchedExperienceName && experienceRanges.length > 0) {
      const expRange = experienceRanges.find((r: any) => {
        const name = r.name || r.RangeName || r.rangename
        return name === fetchedExperienceName
      })
      if (expRange) {
        const id = expRange.id || expRange.RangeID || expRange.rangeid
        setSelectedExperienceRangeId(id)
      }
      setFetchedExperienceName(null)
    }
  }, [experienceRanges, fetchedExperienceName])

  // DB-driven career levels & experience ranges 로드
  useEffect(() => {
    const fetchMeta = async () => {
      try {
        const [cls, ers, jobs] = await Promise.all([
          metaApi.getCareerLevels().catch((e) => {
            console.error('Failed to fetch career levels:', e)
            return { careerlevels: [] }
          }),
          metaApi.getExperienceRanges().catch((e) => {
            console.error('Failed to fetch experience ranges:', e)
            return { experienceranges: [] }
          }),
          metaApi.getDesiredJobs().catch((e) => {
            console.error('Failed to fetch desired jobs:', e)
            return { desiredjobs: [] }
          }),
        ])

        // 응답 데이터 정규화
        const careerList = Array.isArray(cls) ? cls : (cls?.careerlevels || [])
        const expList = Array.isArray(ers) ? ers : (ers?.experienceranges || [])
        const jobList = Array.isArray(jobs) ? jobs : (jobs?.desiredjobs || [])

        setCareerLevels(careerList)
        setExperienceRanges(expList)
        
        // 희망직무를 name만 추출하여 배열로 설정
        const jobNames = jobList.map((j: any) => j.name || j.JobName || '')
        setAllWantedJobs(jobNames)

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
      setScraps([
        { postType: 'Job', targetId: 1, label: '[샘플] Python 백엔드 채용 공고' },
        { postType: 'Job', targetId: 2, label: '[샘플] 데이터 분석 인턴십' },
      ])
      setRecentViews([
        { postType: 'Job', targetId: 1, label: '[샘플] React 개발자 채용' },
        { postType: 'Job', targetId: 2, label: '[샘플] ML 엔지니어 공고' },
      ])

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
          navigate('/login', { replace: true })
          return
        }

        // 로그인했으면 GET /users/me로 전체 프로필 데이터 로드
        try {
          const profileData = await usersApi.getMyProfile()
          if (profileData) {
            if (profileData.name) setName(profileData.name)
            if (profileData.email) setEmail(profileData.email)

            // 커리어 레벨: 서버는 이름(career_level)을 반환하므로 메타에서 ID를 찾아 설정
            if (profileData.career_level) {
              const careerLevel = careerLevels.find((c: any) => {
                const name = c.name || c.CareerName || c.careername
                return name === profileData.career_level
              })
              if (careerLevel) {
                const id = careerLevel.id || careerLevel.CareerLevelID || careerLevel.careerlevelid
                setSelectedCareerLevelId(id)
              }
              else {
                // 메타데이터가 아직 로드되지 않은 경우, 나중에 매핑하기 위해 이름을 저장
                setFetchedCareerName(profileData.career_level)
              }
            }

            if (profileData.experience_range) {
              const expRange = experienceRanges.find((r: any) => {
                const name = r.name || r.RangeName || r.rangename
                return name === profileData.experience_range
              })

              if (expRange) {
                const id = expRange.id || expRange.RangeID || expRange.rangeid
                setSelectedExperienceRangeId(id)
              } else {
                setFetchedExperienceName(profileData.experience_range)
              }
            }

            if (Array.isArray(profileData.skills) && profileData.skills.length > 0) {
              setSelectedStacks(profileData.skills)
            }
            if (Array.isArray(profileData.desired_jobs) && profileData.desired_jobs.length > 0) {
              setSelectedInterests(profileData.desired_jobs)
            }
            if (Array.isArray(profileData.recentviews) && profileData.recentviews.length > 0) {
              // 서버 recentViews는 문자열만 내려오므로, localStorage의 구조화된 recentViews와 라벨 매칭해
              // 가능한 경우 postType/targetId를 보강하여 클릭 이동이 되게 처리
              let localNormalized: RecentViewItem[] = []
              try {
                const raw = localStorage.getItem('recentviews')
                if (raw) {
                  const parsed = JSON.parse(raw)
                  const arr = Array.isArray(parsed) ? parsed : []
                  localNormalized = arr
                    .map((x: any) => {
                      if (typeof x === 'string') return { label: String(x) }
                      if (x && typeof x === 'object') {
                        const postType = String(x.postType ?? x.type ?? '')
                        const targetId = Number(x.targetId ?? x.id)
                        const label = String(x.label ?? x.title ?? '')
                        return { postType: postType === 'Job' || postType === 'Bootcamp' ? postType : undefined, targetId, label }
                      }
                      return null
                    })
                    .filter(Boolean) as RecentViewItem[]
                }
              } catch {
                // ignore
              }

              const merged = profileData.recentviews
                .slice(0, 5)
                .map((x: any) => {
                  const label = String(x)
                  const found = localNormalized.find((y) => y.label === label && y.postType && Number.isFinite(y.targetId))
                  return found ? found : { label }
                })

              setRecentViews(merged)
            } else {
              // 서버에 recentviews가 없으면 로컬스토리지에서 불러와서 사용
              try {
                const raw = localStorage.getItem('recentviews')
                if (raw) {
                  const parsed = JSON.parse(raw)
                  const arr = Array.isArray(parsed) ? parsed : []
                  const normalized = arr
                    .map((x: any) => {
                      if (typeof x === 'string') return { label: String(x) }
                      if (x && typeof x === 'object') {
                        const postType = String(x.postType ?? x.type ?? '')
                        const targetId = Number(x.targetId ?? x.id)
                        const label = String(x.label ?? x.title ?? '')
                        return { postType: postType === 'Job' || postType === 'Bootcamp' ? postType : undefined, targetId, label }
                      }
                      return null
                    })
                    .filter(Boolean) as RecentViewItem[]
                  if (normalized.length > 0) setRecentViews(normalized.slice(0, 5))
                }
              } catch (e) {
                // ignore
              }
            }

            // 스크랩/알림을 별도 API로 가져오기 (서버의 /users/{user_id}/...)
            try {
              const userId = profileData.user_id || profileData.id || null
              if (userId) {
                let scrapsRes: any[] = []
                try {
                  scrapsRes = await usersApi.getMyScraps()
                } catch (e) {
                  scrapsRes = await usersApi.getScraps(userId)
                }
                // scrapsRes는 job_post / bootcamp_post 포함 객체 배열
                const scrapItems = (scrapsRes || [])
                  .map((s: any) => {
                    const postType = String(s?.post_type ?? s?.postType ?? '')
                    if (postType === 'Job') {
                      const targetId = Number(s?.job_post_id ?? s?.jobPostId)
                      const label = String(s?.job_post?.title ?? s?.job_post?.Title ?? '')
                      if (!Number.isFinite(targetId) || !label) return null
                      return { postType: 'Job' as const, targetId, label }
                    }
                    if (postType === 'Bootcamp') {
                      const targetId = Number(s?.bootcamp_post_id ?? s?.bootcampPostId)
                      const label = String(s?.bootcamp_post?.title ?? s?.bootcamp_post?.Title ?? '')
                      if (!Number.isFinite(targetId) || !label) return null
                      return { postType: 'Bootcamp' as const, targetId, label }
                    }
                    return null
                  })
                  .filter(Boolean) as ScrapItem[]
                setScraps(scrapItems.slice(0, 5))

                const notiRes = await usersApi.getNotifications(userId)
                const mappedNoti = (notiRes || []).map((n: any, i: number) => ({
                  id: Date.now() + i,
                  category: n.notification_type || '맞춤형 정보',
                  text: n.notification_type || '설정 알림',
                  timestamp: n.notificationtime || '',
                }))
                setNotifications(mappedNoti.slice(0, 3))
              }
            } catch (e) {
              console.error('Failed to fetch scraps/notifications:', e)
            }
          }
        } catch (e) {
          console.error('Failed to fetch my profile:', e)
        }
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
                <div className="mt-3 relative">
                  <div className="flex flex-wrap gap-2">
                    {selectedInterests.map((job) => (
                      <span
                        key={job}
                        className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-800 ring-1 ring-inset ring-slate-200"
                      >
                        {job}
                        <button
                          onClick={() => toggleWantedJob(job)}
                          className="ml-2 text-slate-400 hover:text-slate-600"
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
                    <div className="absolute inset-x-0 mt-3 w-full z-10">
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
                <div className="mt-3 relative">
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
                    <div className="absolute inset-x-0 mt-3 w-full z-10">
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
              <div className="hidden">
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
                      <li key={`${s.postType}:${s.targetId}:${i}`} className="rounded-md border border-slate-100 bg-white p-3 text-sm text-slate-800">
                        <div className="flex items-start justify-between gap-3">
                          <button
                            type="button"
                            onClick={() => navigate(s.postType === 'Job' ? `/jobs/${s.targetId}` : `/bootcamps/${s.targetId}`)}
                            className="flex-1 text-left"
                          >
                            {s.label}
                          </button>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation()
                              void handleDeleteScrap(i)
                            }}
                            className="shrink-0 text-slate-400 hover:text-red-500"
                            aria-label="스크랩 삭제"
                          >
                            ×
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900">최근 열람 공고</h3>
                {recentviews.length === 0 ? (
                  <div className="mt-2 rounded-xl border border-dashed border-slate-200 bg-white p-3 text-sm text-slate-600">최근 열람한 공고가 없습니다.</div>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {recentviews.map((r, i) => (
                      <li key={`${r.postType ?? 'unknown'}:${String(r.targetId ?? r.label)}:${i}`} className="rounded-md border border-slate-100 bg-white p-3 text-sm text-slate-800">
                        <div className="flex items-start justify-between gap-3">
                          {r.postType && Number.isFinite(r.targetId) ? (
                            <button
                              type="button"
                              onClick={() =>
                                navigate(r.postType === 'Job' ? `/jobs/${r.targetId}` : `/bootcamps/${r.targetId}`)
                              }
                              className="flex-1 text-left"
                            >
                              {r.label}
                            </button>
                          ) : (
                            <div className="flex-1">{r.label}</div>
                          )}
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteRecentView(i)
                            }}
                            className="shrink-0 text-slate-400 hover:text-red-500"
                            aria-label="최근 열람 삭제"
                          >
                            ×
                          </button>
                        </div>
                      </li>
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
