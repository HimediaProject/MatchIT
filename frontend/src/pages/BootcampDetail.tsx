import { useEffect, useRef, useState } from 'react'
import { Link, useParams, useNavigate  } from 'react-router-dom'
import { bootcampApi, type BootcampItem } from '../api/bootcamp'
import { usersApi } from '../api/users'

/**
 * 날짜 포맷팅 함수
 * @param dateString - ISO 날짜 문자열
 * @returns 포맷팅된 날짜 (YYYY.MM.DD)
 */
const formatDate = (dateString: string | null): string => {
  if (!dateString) return '-'

  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}.${month}.${day}`
}

/**
 * 부트캠프 상세 페이지
 */
const BootcampDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [bootcamp, setBootcamp] = useState<BootcampItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const hasFetchedRef = useRef(false)

  const [isScrapped, setIsScrapped] = useState(false)
  const [scrapLoading, setScrapLoading] = useState(false)

  // 커리큘럼 "더보기" 상태
  const [isCurriculumExpanded, setIsCurriculumExpanded] = useState(false)
  const CURRICULUM_PREVIEW_LENGTH = 500

  useEffect(() => {
    if (hasFetchedRef.current) return
    hasFetchedRef.current = true

    const fetchBootcamp = async () => {
      if (!id) {
        setError('부트캠프 ID가 없습니다.')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const data = await bootcampApi.getBootcampDetail(Number(id))
        setBootcamp(data)
        setError(null)
      } catch (err) {
        setError('부트캠프 정보를 불러오는데 실패했습니다.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchBootcamp()
  }, [id])

  useEffect(() => {
    if (!bootcamp?.Title) return
    const numericId = Number(id)
    if (!Number.isFinite(numericId)) return
    const label = `[부트캠프] ${bootcamp.Title}`
    try {
      const raw = localStorage.getItem('recentviews')
      const arr = raw ? JSON.parse(raw) : []
      const current = Array.isArray(arr) ? arr : []

      const normalized = current
        .map((x: any) => {
          if (typeof x === 'string') return { label: String(x) }
          if (x && typeof x === 'object') {
            const postType = String(x.postType ?? x.type ?? '')
            const targetId = Number(x.targetId ?? x.id)
            const lbl = String(x.label ?? x.title ?? '')
            return { postType, targetId, label: lbl }
          }
          return null
        })
        .filter(Boolean) as Array<{ postType?: string; targetId?: number; label: string }>;

      const item = { postType: 'Bootcamp', targetId: numericId, label }
      const next = [
        item,
        ...normalized.filter((x) => !(x?.postType === 'Bootcamp' && Number(x?.targetId) === numericId) && x.label !== label),
      ].slice(0, 5)
      if (numericId > 0) {
        localStorage.setItem('recentviews', JSON.stringify(next))
      }
    } catch {
      try {
        if (numericId > 0) {
          localStorage.setItem('recentviews', JSON.stringify([{ postType: 'Bootcamp', targetId: numericId, label }]))
        }
      } catch {
        // ignore
      }
    }
  }, [bootcamp?.Title, id])

  useEffect(() => {
    if (!id) return
    const numericId = Number(id)
    if (!Number.isFinite(numericId)) return

    let mounted = true
    const load = async () => {
      try {
        const scraps = await usersApi.getMyScraps()
        const found = Array.isArray(scraps)
          ? scraps.some((s: any) => s?.post_type === 'Bootcamp' && Number(s?.bootcamp_post_id) === numericId)
          : false
        if (mounted) setIsScrapped(found)
      } catch {
        // ignore
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [id])

  const toggleScrap = async () => {
    if (!id) return
    const numericId = Number(id)
    if (!Number.isFinite(numericId)) return
    if (scrapLoading) return

    setScrapLoading(true)
    try {
      if (isScrapped) {
        await usersApi.removeMyScrap('Bootcamp', numericId)
        setIsScrapped(false)
      } else {
        await usersApi.addMyScrap('Bootcamp', numericId)
        setIsScrapped(true)
      }
    } catch (e) {
      const msg = String((e as any)?.message ?? e)
      if (msg.includes('401') || msg.includes('403')) {
        if (window.confirm('로그인이 필요합니다. 로그인 페이지로 이동할까요?')) {
          navigate('/login')
        }
      } else {
        window.alert('스크랩 처리에 실패했습니다.')
      }
    } finally {
      setScrapLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">로딩 중...</p>
      </div>
    )
  }

  if (error || !bootcamp) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || '부트캠프를 찾을 수 없습니다.'}</p>
          <Link
            to="/bootcamps"
            className="text-primary-600 hover:underline"
          >
            부트캠프 목록으로 돌아가기
          </Link>
        </div>
      </div>
    )
  }

  // OnlineOffline 표시 변환
  const modeDisplay = bootcamp.OnlineOffline === '혼합형' ? '혼합' : bootcamp.OnlineOffline

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 md:px-6">
        {/* 뒤로 가기 */}
        <div className="mb-6">
          <Link
            to="/bootcamps"
            className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 transition"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            부트캠프 목록으로
          </Link>
        </div>

        {/* 헤더 섹션 */}
        <div className="mb-8 space-y-4">
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm font-semibold text-primary-700">
              {bootcamp.InstituteName}
            </p>

            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-500">
                조회수 {bootcamp.ViewCount.toLocaleString()}
              </span>
            </div>
          </div>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            {bootcamp.Title}
          </h1>

          {/* 기본 정보 카드 */}
          <div className="mb-6 rounded-2xl border border-slate-100 bg-slate-50/80 p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">기본 정보</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-slate-700 mb-1">수강 형태</p>
                <p className="text-sm text-slate-600">{modeDisplay}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-700 mb-1">비용 지원</p>
                <p className="text-sm text-slate-600">{bootcamp.CostSupportType}</p>
              </div>
              {bootcamp.Location && (
                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-1">위치</p>
                  <p className="text-sm text-slate-600">{bootcamp.Location}</p>
                </div>
              )}
            </div>
            <div className="mt-6 flex items-center gap-3">
              {/* 스크랩 버튼 */}
              <button 
                type="button"
                onClick={toggleScrap}
                disabled={scrapLoading}
                className={
                  `flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border transition ` +
                  (isScrapped
                    ? 'border-primary-200 bg-primary-50 text-primary-700 hover:bg-primary-100'
                    : 'border-slate-200 bg-white text-slate-400 hover:bg-slate-50 hover:text-slate-600')
                }
                aria-label="스크랩"
              >
                <svg className="h-6 w-6" fill={isScrapped ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </button>

              {/* 공유하기 버튼 */}
              <button 
                type="button"
                className="h-12 flex-1 rounded-xl bg-primary-50 text-base font-bold text-primary-700 transition hover:bg-primary-100"
              >
                공유하기
              </button>

              {/* 지원하기 버튼 */}
              <a
                href={bootcamp.DetailUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-12 flex-1 items-center justify-center rounded-xl bg-primary-600 text-base font-bold text-white shadow-sm transition hover:bg-primary-700"
              >
                지원하기
              </a>
            </div>
          </div>
        </div>

        {/* 일정 정보 카드 */}
        <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
          <h2 className="mb-4 text-lg font-bold text-slate-900">일정 정보</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-1">시작일</p>
              <p className="text-sm text-slate-600">{formatDate(bootcamp.StartDate)}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-1">마감일</p>
              <p className="text-sm text-slate-600">{formatDate(bootcamp.CloseDate)}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-1">등록일</p>
              <p className="text-sm text-slate-600">{formatDate(bootcamp.RegistrationDate)}</p>
            </div>
          </div>
        </div>

        {/* 커리큘럼 */}
        {bootcamp.EducationContent && (
          <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">커리큘럼</h2>
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap text-sm text-slate-600 leading-relaxed">
                {isCurriculumExpanded
                  ? bootcamp.EducationContent
                  : bootcamp.EducationContent.slice(0, CURRICULUM_PREVIEW_LENGTH)
                }
                {!isCurriculumExpanded && bootcamp.EducationContent.length > CURRICULUM_PREVIEW_LENGTH && '...'}
              </p>
              {bootcamp.EducationContent.length > CURRICULUM_PREVIEW_LENGTH && (
                <button
                  onClick={() => setIsCurriculumExpanded(!isCurriculumExpanded)}
                  className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-primary-600 hover:text-primary-700 transition"
                >
                  {isCurriculumExpanded ? (
                    <>
                      접기
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                    </>
                  ) : (
                    <>
                      더보기
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        )}

        {/* 자격요건 */}
        {bootcamp.Qualification && (
          <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">자격요건</h2>
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap text-sm text-slate-600 leading-relaxed">
                {bootcamp.Qualification}
              </p>
            </div>
          </div>
        )}

        {/* 혜택 */}
        {bootcamp.Benefits && (
          <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">혜택</h2>
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap text-sm text-slate-600 leading-relaxed">
                {bootcamp.Benefits}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BootcampDetailPage