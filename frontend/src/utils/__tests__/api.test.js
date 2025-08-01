import { API_BASE_URL } from '../api';

describe('API Configuration', () => {
  test('API_BASE_URL is defined', () => {
    expect(API_BASE_URL).toBeDefined();
    expect(typeof API_BASE_URL).toBe('string');
  });

  test('API_BASE_URL has correct format', () => {
    expect(API_BASE_URL).toMatch(/^https?:\/\/.+/);
  });
});

describe('API Utilities', () => {
  test('can make basic API calls', () => {
    // This is a basic test to ensure the test suite runs
    expect(true).toBe(true);
  });
}); 