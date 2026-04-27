import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  full_name: string
  is_superadmin: boolean
}

interface AuthState {
  token: string | null
  user: User | null
  activeOrgId: string | null
  orgs: Array<{ id: string; name: string; slug: string }>
  setAuth: (token: string, user: User) => void
  setActiveOrg: (orgId: string) => void
  setOrgs: (orgs: AuthState['orgs']) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      activeOrgId: null,
      orgs: [],
      setAuth: (token, user) => set({ token, user }),
      setActiveOrg: (orgId) => set({ activeOrgId: orgId }),
      setOrgs: (orgs) => set({ orgs }),
      logout: () => set({ token: null, user: null, activeOrgId: null, orgs: [] }),
    }),
    { name: 'nexiss-auth' }
  )
)
