const API_BASE_URL = "http://localhost:8000"; // dev
// const API_BASE_URL2 = "server:8000"; // docker

export const authApi = {
  getSocialLoginUrl(provider: string) {
    return `${API_BASE_URL}/auth/${provider}/login`;
  },
};