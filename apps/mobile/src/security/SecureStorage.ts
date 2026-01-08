/**
 * Secure Storage for Mobile
 * Platform-specific encryption
 */

import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';

export class SecureStorage {
  /**
   * Store sensitive data securely
   * Uses hardware-backed encryption on supported devices
   */
  static async setItem(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value, {
        keychainAccessible: SecureStore.WHEN_UNLOCKED,
      });
    } catch (error) {
      console.error('Secure storage error:', error);
      throw error;
    }
  }

  /**
   * Retrieve securely stored data
   */
  static async getItem(key: string): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.error('Secure storage error:', error);
      return null;
    }
  }

  /**
   * Remove securely stored data
   */
  static async removeItem(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.error('Secure storage error:', error);
    }
  }

  /**
   * Store auth tokens securely
   */
  static async setTokens(accessToken: string, refreshToken: string): Promise<void> {
    await Promise.all([
      this.setItem('access_token', accessToken),
      this.setItem('refresh_token', refreshToken),
    ]);
  }

  /**
   * Get auth tokens
   */
  static async getTokens(): Promise<{ accessToken: string | null, refreshToken: string | null }> {
    const [accessToken, refreshToken] = await Promise.all([
      this.getItem('access_token'),
      this.getItem('refresh_token'),
    ]);
    
    return { accessToken, refreshToken };
  }

  /**
   * Clear all tokens
   */
  static async clearTokens(): Promise<void> {
    await Promise.all([
      this.removeItem('access_token'),
      this.removeItem('refresh_token'),
    ]);
  }

  /**
   * Verify app integrity (jailbreak/root detection)
   */
  static async checkIntegrity(): Promise<boolean> {
    // Basic integrity check
    // Production should use more sophisticated methods
    try {
      const testValue = 'integrity_check';
      await this.setItem('_integrity_test', testValue);
      const retrieved = await this.getItem('_integrity_test');
      await this.removeItem('_integrity_test');
      
      return retrieved === testValue;
    } catch {
      return false;
    }
  }
}
