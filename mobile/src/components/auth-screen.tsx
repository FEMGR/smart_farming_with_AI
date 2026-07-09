import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import { useAuth } from '@/context/AuthContext';
import { ThemedText } from './themed-text';
import { ThemedView } from './themed-view';
import { Spacing } from '@/constants/theme';
import { getApiBaseUrl, setApiBaseUrl } from '@/services/api';

export function AuthScreen() {
  const { login, register } = useAuth();
  
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // API Config Modal state
  const [configVisible, setConfigVisible] = useState(false);
  const [apiUrl, setApiUrl] = useState('');

  useEffect(() => {
    async function loadUrl() {
      const url = await getApiBaseUrl();
      setApiUrl(url);
    }
    loadUrl();
  }, []);

  const handleAuth = async () => {
    if (!email.trim() || !password.trim()) {
      setErrorMsg('Please fill in all fields');
      return;
    }
    
    setErrorMsg(null);
    setAuthLoading(true);
    try {
      if (isLogin) {
        await login(email.trim(), password);
      } else {
        await register(email.trim(), password);
      }
    } catch (e: any) {
      setErrorMsg(e.message || 'Authentication failed');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSaveUrl = async () => {
    if (!apiUrl.trim()) return;
    try {
      await setApiUrl(apiUrl.trim());
      await setApiBaseUrl(apiUrl.trim());
      setConfigVisible(false);
      Alert.alert('Success', 'API URL updated successfully');
    } catch (e) {
      Alert.alert('Error', 'Failed to save API URL');
    }
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        {/* Settings button */}
        <TouchableOpacity
          style={styles.settingsBtn}
          onPress={() => setConfigVisible(true)}
        >
          <SymbolView name="gearshape.fill" size={24} tintColor="#10B981" />
        </TouchableOpacity>

        <View style={styles.header}>
          <SymbolView name="leaf.fill" size={64} tintColor="#10B981" />
          <ThemedText type="subtitle" style={styles.title}>
            Smart Farming
          </ThemedText>
          <ThemedText themeColor="textSecondary" style={styles.subtitle}>
            Manage your urban farm dashboard
          </ThemedText>
        </View>

        <ThemedView type="backgroundElement" style={styles.formCard}>
          <ThemedText type="smallBold" style={styles.formTitle}>
            {isLogin ? 'Sign In to Your Farm' : 'Create Farm Account'}
          </ThemedText>

          {errorMsg && (
            <ThemedView style={styles.errorContainer}>
              <ThemedText style={styles.errorText}>{errorMsg}</ThemedText>
            </ThemedView>
          )}

          <TextInput
            style={styles.input}
            placeholder="Email address"
            placeholderTextColor="#888"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />

          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor="#888"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoCapitalize="none"
          />

          <TouchableOpacity
            style={styles.button}
            onPress={handleAuth}
            disabled={authLoading}
          >
            {authLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <ThemedText style={styles.buttonText}>
                {isLogin ? 'Sign In' : 'Register'}
              </ThemedText>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.switchBtn}
            onPress={() => {
              setIsLogin(!isLogin);
              setErrorMsg(null);
            }}
          >
            <ThemedText type="linkPrimary">
              {isLogin
                ? "Don't have an account? Register"
                : 'Already have an account? Sign In'}
            </ThemedText>
          </TouchableOpacity>
        </ThemedView>
      </SafeAreaView>

      {/* Dynamic API Config Modal */}
      <Modal
        visible={configVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setConfigVisible(false)}
      >
        <View style={styles.modalBg}>
          <ThemedView type="backgroundElement" style={styles.modalCard}>
            <ThemedText type="smallBold" style={styles.modalTitle}>
              Configure API Target
            </ThemedText>
            
            <ThemedText type="small" themeColor="textSecondary" style={styles.modalDesc}>
              Set the URL of your FastAPI backend service.
            </ThemedText>

            <TextInput
              style={styles.input}
              placeholder="http://10.0.2.2:8000"
              placeholderTextColor="#888"
              value={apiUrl}
              onChangeText={setApiUrl}
              autoCapitalize="none"
              autoCorrect={false}
            />

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.modalBtn, styles.cancelBtn]}
                onPress={() => setConfigVisible(false)}
              >
                <ThemedText style={styles.modalBtnText}>Cancel</ThemedText>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalBtn, styles.saveBtn]}
                onPress={handleSaveUrl}
              >
                <ThemedText style={[styles.modalBtnText, { color: '#fff' }]}>
                  Save
                </ThemedText>
              </TouchableOpacity>
            </View>
          </ThemedView>
        </View>
      </Modal>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
    paddingHorizontal: Spacing.four,
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingsBtn: {
    position: 'absolute',
    top: Spacing.four,
    right: Spacing.four,
    padding: Spacing.two,
  },
  header: {
    alignItems: 'center',
    marginBottom: Spacing.five,
  },
  title: {
    fontWeight: 'bold',
    marginTop: Spacing.two,
  },
  subtitle: {
    fontSize: 14,
    marginTop: Spacing.one,
  },
  formCard: {
    width: '100%',
    maxWidth: 400,
    padding: Spacing.four,
    borderRadius: Spacing.four,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 3,
  },
  formTitle: {
    fontSize: 18,
    marginBottom: Spacing.three,
    textAlign: 'center',
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    padding: Spacing.two,
    borderRadius: Spacing.two,
    marginBottom: Spacing.three,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 12,
    textAlign: 'center',
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: Spacing.two,
    paddingHorizontal: Spacing.three,
    marginBottom: Spacing.three,
    fontSize: 16,
    color: '#000',
    backgroundColor: '#fff',
  },
  button: {
    height: 48,
    backgroundColor: '#10B981',
    borderRadius: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing.two,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  switchBtn: {
    marginTop: Spacing.three,
    alignItems: 'center',
  },
  modalBg: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    padding: Spacing.four,
  },
  modalCard: {
    width: '100%',
    maxWidth: 360,
    padding: Spacing.four,
    borderRadius: Spacing.three,
  },
  modalTitle: {
    fontSize: 18,
    marginBottom: Spacing.two,
  },
  modalDesc: {
    marginBottom: Spacing.three,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: Spacing.two,
  },
  modalBtn: {
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.four,
    borderRadius: Spacing.one,
  },
  cancelBtn: {
    backgroundColor: '#E5E7EB',
  },
  saveBtn: {
    backgroundColor: '#10B981',
  },
  modalBtnText: {
    fontWeight: 'bold',
    fontSize: 14,
    color: '#374151',
  },
});
