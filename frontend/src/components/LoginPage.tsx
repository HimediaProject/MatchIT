type NavigateFunction = (page: string) => void;

interface LoginPageProps {
  onNavigate: NavigateFunction;
}

export default function LoginPage({ onNavigate }: LoginPageProps) {
  const [isLoading, setIsLoading] = useState(false);

  // 소셜 로그인 핸들러
  const handleSocialLogin = async (provider: string) => {
    try {
      setIsLoading(true);
      window.location.href = authApi.getSocialLoginUrl(provider);
      // const response = await fetch(authApi.getSocialLoginUrl(provider));
      // if (response.url) {
      //   window.location.href = response.url; // 실제 인증 페이지로 이동
      // } else {
      //   alert("소셜 로그인 URL을 가져올 수 없습니다.");
      // }
    } catch (e) {
      console.error(e);
      alert("소셜 로그인 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-200 p-8">
      <div className="w-full max-w-lg">
        {/* Service Logo & Title */}
        <div className="text-center mb-10">
          <div className="w-28 h-28 border-2 border-gray-900 mx-auto mb-5 flex items-center justify-center bg-white">
            <div className="text-4xl text-gray-400">×</div>
          </div>
          <div className="mb-2 font-bold text-xl">MatchIT</div>
          <p className="text-sm text-gray-600">
            기술 스택 기반 채용·교육 매칭 플랫폼
          </p>
        </div>

        {/* Login Box */}
        <div className="border-2 border-gray-900 bg-white p-12">
          <div className="text-center mb-8">
            <div className="mb-2 font-semibold">소셜 계정으로 로그인</div>
          </div>

          {/* Social Buttons */}
          <div className="space-y-3">
            {/* GOOGLE */}
            <button
              disabled={isLoading}
              onClick={() => handleSocialLogin("google")}
              className="w-full py-3 border border-gray-900 bg-gray-50 hover:bg-gray-100 flex items-center gap-4 px-6 disabled:opacity-50"
            >
              <div className="w-7 h-7 border border-gray-600 flex items-center justify-center bg-white">
                <span className="text-xs">G</span>
              </div>
              <span className="flex-1 text-left">Google 계정으로 계속</span>
            </button>

            {/* KAKAO */}
            <button
              disabled={isLoading}
              onClick={() => handleSocialLogin("kakao")}
              className="w-full py-3 border border-gray-900 bg-gray-50 hover:bg-gray-100 flex items-center gap-4 px-6 disabled:opacity-50"
            >
              <div className="w-7 h-7 border border-gray-600 flex items-center justify-center bg-white">
                <span className="text-xs">K</span>
              </div>
              <span className="flex-1 text-left">Kakao 계정으로 계속</span>
            </button>

            {/* NAVER */}
            <button
              disabled={isLoading}
              onClick={() => handleSocialLogin("naver")}
              className="w-full py-3 border border-gray-900 bg-gray-50 hover:bg-gray-100 flex items-center gap-4 px-6 disabled:opacity-50"
            >
              <div className="w-7 h-7 border border-gray-600 flex items-center justify-center bg-white">
                <span className="text-xs">N</span>
              </div>
              <span className="flex-1 text-left">Naver 계정으로 계속</span>
            </button>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-600 mb-2">
            로그인 시 아래 약관에 동의하게 됩니다
          </p>
          <div className="flex justify-center gap-3 text-xs">
            <button className="underline">이용약관</button>
            <span>|</span>
            <button className="underline">개인정보처리방침</button>
          </div>
        </div>

        {/* Demo Access */}
        <div className="mt-8 border border-gray-500 bg-gray-100 p-4">
          <p className="text-xs text-center mb-2">[ Wireframe Demo ]</p>
          <button
            onClick={() => onNavigate("home")}
            className="w-full py-2 border border-gray-900 bg-gray-900 text-white hover:bg-gray-700"
          >
            데모 보기 →
          </button>
        </div>
      </div>
    </div>
  );
}