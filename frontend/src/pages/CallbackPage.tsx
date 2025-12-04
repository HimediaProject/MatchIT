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
    // provider가 state를 요구하는 경우에만 쿼리에 포함
    const qs = new URLSearchParams({ code });
    if (state) qs.set("state", state);

    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/auth/${provider}/callback?${qs.toString()}`,
      { method: "GET", credentials: "include" } // 서버가 쿠키를 Set-Cookie로 내려줄 수도 있으므로 credentials 포함
    );

    if (!res.ok) throw new Error("로그인 실패");

    const data = await res.json();
    // data.accessToken, data.refreshToken, data.user?.name / email 등 가정

    // 1) Header가 참조하는 플래그 저장
    localStorage.setItem("isLoggedIn", "true");

    // 2) 선택: 프론트가 직접 토큰을 보관할 경우
    if (data.accessToken) {
      localStorage.setItem("access_token", data.accessToken);
      // Header는 쿠키 'kakao_access_token'을 읽으므로 동일 이름으로 세팅
      // provider가 kakao가 아니더라도, Header 코드와 맞추려면 동일 키를 사용하거나 Header 쪽 조건을 일반화해야 합니다.
      document.cookie = `kakao_access_token=${data.accessToken}; path=/;`;
    }

    // 3) 선택: 사용자 정보 저장
    if (data.user?.name) localStorage.setItem("userName", data.user.name);
    if (data.user?.email) localStorage.setItem("userEmail", data.user.email);

    // 4) 이동
    navigate("/");
  } catch (err) {
    console.error(err);
    alert("로그인 처리 중 오류 발생");
    navigate("/");
  }
};

fetchToken();