const API_BASE_URL = "http://localhost:8000";   // dev
// const API_BASE_URL2 = "server:8000";         // docker

export const authApi = {
  getSocialLoginUrl(provider: string) {
    return `${API_BASE_URL}/auth/${provider}/login`;
  },
};

export const searchApi = {
  async search(keyword: string) {
    const url = `${API_BASE_URL}/search?keyword=${encodeURIComponent(keyword)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Search request failed: ${res.status}`);
    return res.json();
  },
};

export const skillsApi = {
  async getAllSkills() {
    const url = `${API_BASE_URL}/skills/all`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Get all skills failed: ${res.status}`);
    return res.json();
  },

  async autocomplete(query: string) {
    const url = `${API_BASE_URL}/skills?query=${encodeURIComponent(query)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Skills autocomplete failed: ${res.status}`);
    return res.json();
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

export const metaApi = {
  async getCareerLevels() {
    const url = `${API_BASE_URL}/careerlevels`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Get career levels failed: ${res.status}`);
    return res.json();
  },

  async getExperienceRanges() {
    const url = `${API_BASE_URL}/experienceranges`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Get experience ranges failed: ${res.status}`);
    return res.json();
  },
};