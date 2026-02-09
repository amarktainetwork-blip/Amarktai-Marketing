import { SignUp } from '@clerk/clerk-react';
import { Link } from 'react-router-dom';
import { Rocket, Check } from 'lucide-react';

export default function RegisterPage() {
  const benefits = [
    '14-day free trial',
    'No credit card required',
    'Cancel anytime',
    'Full feature access',
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-4xl grid lg:grid-cols-2 gap-8 items-center">
          {/* Left side - Benefits */}
          <div className="hidden lg:block">
            <Link to="/" className="inline-flex items-center space-x-2 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                Amarktai
              </span>
            </Link>
            <h1 className="text-3xl font-bold mb-4">
              Start Your Free Trial Today
            </h1>
            <p className="text-gray-600 mb-8">
              Join thousands of founders who are scaling their marketing with AI-powered automation.
            </p>
            <ul className="space-y-4">
              {benefits.map((benefit, i) => (
                <li key={i} className="flex items-center">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3">
                    <Check className="w-4 h-4 text-green-600" />
                  </div>
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Right side - Sign up form */}
          <div>
            <div className="lg:hidden text-center mb-8">
              <Link to="/" className="inline-flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Rocket className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                  Amarktai
                </span>
              </Link>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <SignUp 
                routing="path"
                path="/register"
                signInUrl="/login"
                redirectUrl="/dashboard"
                appearance={{
                  elements: {
                    formButtonPrimary: 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700',
                    footerActionLink: 'text-violet-600 hover:text-violet-700',
                  }
                }}
              />
            </div>
            
            <p className="text-center mt-6 text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-violet-600 hover:text-violet-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
