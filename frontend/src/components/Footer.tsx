const Footer = () => {
  return (
    <footer className="border-t border-slate-100 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-6 text-sm text-slate-500 md:flex-row md:items-center md:justify-between md:px-6">
        <div>
          <p className="font-semibold text-slate-700">MatchIT</p>
          <p className="mt-1 text-xs text-slate-500">
            내 스택과 커리어에 맞춘 채용공고·부트캠프 추천 플랫폼
          </p>
        </div>
        <div className="flex items-center gap-4">
          <a className="transition hover:text-primary-600" href="#">
            서비스 소개
          </a>
          <a className="transition hover:text-primary-600" href="#">
            이용약관
          </a>
          <a className="transition hover:text-primary-600" href="#">
            개인정보 처리방침
          </a>
        </div>
      </div>
    </footer>
  )
}

export default Footer
