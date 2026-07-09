import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

const STORAGE_KEYS = {
  API_URL: 'smart_farming_api_url',
  TOKEN: 'smart_farming_token',
  EMAIL: 'smart_farming_email',
};

const DEFAULT_BASE_URL = Platform.select({
  android: 'http://10.0.2.2:8000',
  default: 'http://localhost:8000',
});

let cachedBaseUrl: string | null = null;
let cachedToken: string | null = null;
let cachedEmail: string | null = null;

export async function getApiBaseUrl(): Promise<string> {
  if (cachedBaseUrl) return cachedBaseUrl;
  try {
    const saved = await AsyncStorage.getItem(STORAGE_KEYS.API_URL);
    cachedBaseUrl = saved || DEFAULT_BASE_URL;
  } catch {
    cachedBaseUrl = DEFAULT_BASE_URL;
  }
  return cachedBaseUrl;
}

export async function setApiBaseUrl(url: string): Promise<void> {
  const formattedUrl = url.trim().replace(/\/$/, '');
  cachedBaseUrl = formattedUrl;
  await AsyncStorage.setItem(STORAGE_KEYS.API_URL, formattedUrl);
}

export async function getToken(): Promise<string | null> {
  if (cachedToken) return cachedToken;
  try {
    cachedToken = await AsyncStorage.getItem(STORAGE_KEYS.TOKEN);
  } catch {
    cachedToken = null;
  }
  return cachedToken;
}

export async function setToken(token: string | null): Promise<void> {
  cachedToken = token;
  if (token) {
    await AsyncStorage.setItem(STORAGE_KEYS.TOKEN, token);
  } else {
    await AsyncStorage.removeItem(STORAGE_KEYS.TOKEN);
  }
}

export async function getEmail(): Promise<string | null> {
  if (cachedEmail) return cachedEmail;
  try {
    cachedEmail = await AsyncStorage.getItem(STORAGE_KEYS.EMAIL);
  } catch {
    cachedEmail = null;
  }
  return cachedEmail;
}

export async function setEmail(email: string | null): Promise<void> {
  cachedEmail = email;
  if (email) {
    await AsyncStorage.setItem(STORAGE_KEYS.EMAIL, email);
  } else {
    await AsyncStorage.removeItem(STORAGE_KEYS.EMAIL);
  }
}

export async function clearAllStorage(): Promise<void> {
  cachedToken = null;
  cachedEmail = null;
  await AsyncStorage.removeItem(STORAGE_KEYS.TOKEN);
  await AsyncStorage.removeItem(STORAGE_KEYS.EMAIL);
}

export interface ApiRequestOptions {
  method?: string;
  body?: any;
  params?: Record<string, string | number | boolean>;
  auth?: boolean;
}

export async function apiRequest(path: string, options: ApiRequestOptions = {}): Promise<any> {
  const { method = 'GET', body, params, auth = true } = options;
  const baseUrl = await getApiBaseUrl();
  const token = await getToken();

  let url = `${baseUrl}${path}`;
  if (params) {
    const query = Object.entries(params)
      .filter(([_, val]) => val !== undefined && val !== null)
      .map(([key, val]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(val))}`)
      .join('&');
    if (query) {
      url += `?${query}`;
    }
  }

  const headers: Record<string, string> = {};

  if (body instanceof FormData) {
    // Let fetch automatically set boundaries for FormData
  } else if (body) {
    headers['Content-Type'] = 'application/json';
  }

  if (auth && token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const requestConfig: RequestInit = {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  };

  try {
    const response = await fetch(url, requestConfig);

    if (response.status === 204) {
      return null;
    }

    const text = await response.text();
    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }

    if (!response.ok) {
      const errorMsg = data?.detail || data || `${response.status} Error`;
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    }

    return data;
  } catch (error: any) {
    if (error.message && error.message.includes('Failed to fetch')) {
      throw new Error(`Cannot reach API at ${baseUrl}. Please check connection or URL.`);
    }
    throw error;
  }
}
