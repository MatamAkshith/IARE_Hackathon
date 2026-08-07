import React from 'react';
import AuthLayout from '../components/AuthLayout';
import LoginForm from '../components/LoginForm';

export default function Login() {
  return (
    <AuthLayout>
      {/* Login Form component */}
      <LoginForm />

      {/* Footer / Info inside the card */}
      <div className="mt-8 pt-4 border-t border-slate-800/40 text-center space-y-1 text-[10px] text-slate-500 font-mono">
        <div>ThreatLens Security Suite v1.2.4</div>
        <div>AUTHORIZED OPERATORS ONLY • ALL ACTIONS LOGGED</div>
        <div className="text-[9px] text-slate-600">
          Copyright &copy; {new Date().getFullYear()} ThreatLens Inc. All rights reserved.
        </div>
      </div>
    </AuthLayout>
  );
}
