import { create } from 'zustand'
import { authApi } from '../services/apiService'

export interface User {
  id: number
  name: string
  email: string
  role: 'user' | 'admin'
  careerLevel?: string
  skills?: string[]
  desiredJobs?: string[]
}

interface AuthStore {
  user: User | null
  isLoading: boolean
  isLoggedIn: boolean
  setUser: (user: User | null) => void
  logout: () => void
  fetchCurrentUser: () => Promise<void>
  updateUserRole: (userId: number, role: 'user' | 'admin') => void
}

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  isLoading: false,
  isLoggedIn: false,

  setUser: (user) => {
    set({ user, isLoggedIn: !!user })
  },

  logout: () => {
    set({ user: null, isLoggedIn: false })
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true })
    try {
      const result = await authApi.getCurrentUser()
      if (result.isLoggedIn && result.user) {
        set({
          user: {
            id: result.user.user_id || result.user.id,
            name: result.user.name || '',
            email: result.user.email || '',
            role: result.user.role || 'user',
            careerLevel: result.user.career_level,
            skills: result.user.skills || [],
            desiredJobs: result.user.desired_jobs || [],
          },
          isLoggedIn: true,
        })
      } else {
        set({ user: null, isLoggedIn: false })
      }
    } catch (error) {
      console.error('📢 현재 사용자를 가져오지 못했습니다:', error)
      set({ user: null, isLoggedIn: false })
    } finally {
      set({ isLoading: false })
    }
  },

  updateUserRole: (userId, role) => {
    set((state) => ({
      user: state.user && state.user.id === userId ? { ...state.user, role } : state.user,
    }))
  },
}))
