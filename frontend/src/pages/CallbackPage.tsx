import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function CallbackPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = params.get("code");
    const state = params.get("state");
    const provider = params.get("provider");

    if (!code || !provider) {
      alert("잘못된 접근입니다.");
      navigate("/");
      return;
    }

    const fetchToken = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_API_URL}/auth/${provider}/callback?code=${code}&state=${state}`,
          { method: "GET" }
        );

        if (!res.ok) throw new Error("로그인 실패");

        const data = await res.json();

        // ⭐ 여기서 토큰 저장
        localStorage.setItem("access_token", data.accessToken);

        // 원한다면 리프레시 토큰도 저장
        // localStorage.setItem("refresh_token", data.refreshToken);

        navigate("/"); // 로그인 완료 → 메인으로 이동
      } catch (err) {
        console.error(err);
        alert("로그인 처리 중 오류 발생");
        navigate("/");
      }
    };

    fetchToken();
  }, []);

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      🔄 로그인 처리 중입니다. 잠시만 기다려 주세요...
    </div>
  );
}