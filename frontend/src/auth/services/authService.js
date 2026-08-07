import { encodeMockToken } from '../utils/jwt';
import { ROLES } from '../utils/roles';

// Mock database users
const MOCK_USERS = [
  {
    email: 'admin@threatlens.io',
    password: 'adminPassword123!',
    name: 'Sarah Connor',
    role: ROLES.ADMIN,
    title: 'Chief Security Officer'
  },
  {
    email: 'analyst@threatlens.io',
    password: 'analystPassword123!',
    name: 'John Connor',
    role: ROLES.ANALYST,
    title: 'Senior SOC Analyst'
  },
  {
    email: 'auditor@threatlens.io',
    password: 'auditorPassword123!',
    name: 'Marcus Wright',
    role: ROLES.AUDITOR,
    title: 'External Auditor'
  }
];

// Simulated network delay helper
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Authentication service simulating backend endpoints
 */
export const authService = {
  /**
   * Log in a user with email and password
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<Object>} Response with token and user data
   */
  login: async (email, password) => {
    await delay(1200); // Simulate API latency
    
    const formattedEmail = email.toLowerCase().trim();
    const user = MOCK_USERS.find(u => u.email === formattedEmail);
    
    if (!user) {
      throw new Error('Access Denied: Invalid credentials or account does not exist.');
    }
    
    if (user.password !== password) {
      throw new Error('Access Denied: Invalid credentials.');
    }
    
    // Generate a mock JWT token
    const tokenPayload = {
      email: user.email,
      name: user.name,
      role: user.role,
      title: user.title
    };
    
    const token = encodeMockToken(tokenPayload);
    
    return {
      token,
      user: {
        email: user.email,
        name: user.name,
        role: user.role,
        title: user.title
      }
    };
  },

  /**
   * Request password reset code
   * @param {string} email 
   * @returns {Promise<boolean>}
   */
  forgotPassword: async (email) => {
    await delay(1000); // Simulate latency
    
    const formattedEmail = email.toLowerCase().trim();
    const userExists = MOCK_USERS.some(u => u.email === formattedEmail);
    
    if (!userExists) {
      throw new Error('No account associated with this email address.');
    }
    
    return true; // Return true to signify check and process succeeded
  },

  /**
   * Get current authenticated user details from token
   * @param {string} token 
   * @returns {Promise<Object>}
   */
  getCurrentUser: async (token) => {
    await delay(300); // Mock instant verification
    return tokenPayload;
  }
};
