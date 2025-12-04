const API_BASE_URL = "http://localhost:8000";   // dev
// const API_BASE_URL2 = "server:8000";         // docker

export const authApi = {
  getSocialLoginUrl(provider: string) {
    return `${API_BASE_URL}/auth/${provider}/login`;
  },
  async getCurrentUser() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/kakao/me`, {
        method: 'GET',
        credentials: 'include', // 쿠키 포함
      })
      if (!response.ok) {
        return { isLoggedIn: false, user: null }
      }
      return await response.json()
    } catch (error) {
      console.error('Failed to fetch current user:', error)
      return { isLoggedIn: false, user: null }
    }
  },
};