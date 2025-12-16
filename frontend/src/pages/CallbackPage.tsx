import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { authApi } from "../api/auth";

export default function CallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // API를 호출하여 로그인 상태를 미리 확인
        // 이렇게 하면 백엔드에서 쿠키를 설정한 후 프론트가 상태를 확인할 수 있음
        const result = await authApi.getCurrentUser();
        console.log("Callback - Login status:", result);

        if (result.isLoggedIn) {
          console.log("로그인 성공:", result.user);
        }

        // 신규 회원가입인 경우 프로필 페이지로, 아니면 홈으로 이동
        const isSignup = searchParams.get('signup') === 'true';
        const targetPath = isSignup ? '/profile' : '/';

        // 짧은 딜레이 후 이동
        setTimeout(() => {
          navigate(targetPath, { replace: true });
        }, 500);
      } catch (error) {
        console.error("Callback 처리 중 오류:", error);
        // 에러가 나도 홈으로 이동
        navigate("/", { replace: true });
      }
    };

    handleCallback();
  }, [navigate, searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-white">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <div className="w-14 h-14 rounded-full border-4 border-primary-200 border-t-primary-600 animate-spin"></div>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">로그인 중입니다</h1>
        <p className="text-slate-600">잠시만 기다려주세요...</p>
      </div>
    </div>
  );
}