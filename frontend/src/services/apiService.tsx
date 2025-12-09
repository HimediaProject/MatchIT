const API_BASE_URL = "http://localhost:8000";   // dev
// const API_BASE_URL2 = "server:8000";         // docker

export const authApi = {
  getSocialLoginUrl(provider: string) {
    return `${API_BASE_URL}/auth/${provider}/login?prompt=login`;
  },

  async getCurrentUser() {
    try {
      console.log('[API] getCurrentUser 호출 시작')
      const response = await fetch(`${API_BASE_URL}/auth/kakao/me`, {
        method: 'GET',
        credentials: 'include', // 쿠키 포함
      })
      
      console.log('[API] 응답 상태:', response.status)
      
      if (!response.ok) {
        console.warn('[API] 응답 실패 (상태 코드):', response.status)
        return { isLoggedIn: false, user: null }
      }
      
      const data = await response.json()
      console.log('[API] 응답 데이터:', data)
      return data
    } catch (error) {
      console.error('[API] getCurrentUser 중 오류:', error)
      return { isLoggedIn: false, user: null }
    }
  },
};

export const searchApi = {
  async search(keyword: string) {
    const url = `${API_BASE_URL}/search?keyword=${encodeURIComponent(keyword)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Search request failed: ${res.status}`);
    return res.json();
  },

  async searchWithFilters(params: {
    keyword?: string;
    skills?: string[];
    source?: '전체' | '채용' | '부트캠프';
    careerLevelId?: number;
    experienceRangeId?: number;
    limit?: number;
    randomOrder?: boolean;
  }) {
    const queryParams = new URLSearchParams();
    
    if (params.keyword) {
      queryParams.append('keyword', params.keyword);
    }
    if (params.skills && params.skills.length > 0) {
      params.skills.forEach(skill => {
        queryParams.append('skills', skill);
      });
    }
    if (params.source && params.source !== '전체') {
      queryParams.append('source', params.source);
    }
    if (params.careerLevelId) {
      queryParams.append('career_level_id', params.careerLevelId.toString());
    }
    if (params.experienceRangeId) {
      queryParams.append('experience_range_id', params.experienceRangeId.toString());
    }
    if (params.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    if (params.randomOrder) {
      queryParams.append('random_order', 'true');
    }

    const url = `${API_BASE_URL}/search?${queryParams.toString()}`;
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

export const chatApi = {
  async sendMessage(messages: Array<{ role: string; content: string }>, model?: string) {
    const url = `${API_BASE_URL}/chat/`;
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        ...(model && { model }),
      }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Chat request failed: ${res.status}`);
    }
    return res.json();
  },

  async checkHealth() {
    const url = `${API_BASE_URL}/chat/health`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Chat health check failed: ${res.status}`);
    return res.json();
  },
};