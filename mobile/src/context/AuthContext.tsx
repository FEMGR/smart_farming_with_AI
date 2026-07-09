import React, { createContext, useContext, useState, useEffect } from 'react';
import { getToken, getEmail, setToken, setEmail, clearAllStorage, getApiBaseUrl } from '../services/api';

interface AuthContextType {
  token: string | null;
  email: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [email, setEmailState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      try {
        const savedToken = await getToken();
        const savedEmail = await getEmail();
        if (savedToken && savedEmail) {
          setTokenState(savedToken);
          setEmailState(savedEmail);
        }
      } catch (e) {
        console.error('Failed to restore session', e);
      } finally {
        setLoading(false);
      }
    }
    restoreSession();
  }, []);

  const login = async (userEmail: string, pass: string) => {
    setLoading(true);
    try {
      const baseUrl = await getApiBaseUrl();
      const response = await fetch(`${baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(userEmail)}&password=${encodeURIComponent(pass)}`,
      });

      if (!response.ok) {
        const text = await response.text();
        let errDetail = 'Invalid credentials';
        try {
          const parsed = JSON.parse(text);
          errDetail = parsed.detail || errDetail;
        } catch {}
        throw new Error(errDetail);
      }

      const data = await response.json();
      const accessToken = data.access_token;

      await setToken(accessToken);
      await setEmail(userEmail);
      setTokenState(accessToken);
      setEmailState(userEmail);
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userEmail: string, pass: string) => {
    setLoading(true);
    try {
      const baseUrl = await getApiBaseUrl();
      const response = await fetch(`${baseUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: userEmail, password: pass }),
      });

      if (!response.ok) {
        const text = await response.text();
        let errDetail = 'Registration failed';
        try {
          const parsed = JSON.parse(text);
          errDetail = parsed.detail || errDetail;
        } catch {}
        throw new Error(errDetail);
      }

      // Automatically login after successful registration
      await login(userEmail, pass);
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await clearAllStorage();
      setTokenState(null);
      setEmailState(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ token, email, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
