import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AuthUser {
  id: string
  email: string
  full_name: string
  is_superuser: boolean   // matches backend field name
}

interface AuthState {
  token: string | null
  user: AuthUser | null
  activeOrgId: string | null
  orgs: Array<{ id: string; name: string; slug: string }>
  setAuth: (token: string, user: AuthUser) => void
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
