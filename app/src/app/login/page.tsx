import { SignIn } from '@clerk/clerk-react';
import { Link, useNavigate } from 'react-router-dom';
import { Rocket, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useDemoAuth } from '@/App';

// Check if we have a valid Clerk key
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const isValidClerkKey = clerkPubKey && clerkPubKey.startsWith('pk_');

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useDemoAuth();

  const handleDemoLogin = () => {
    login();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <Link to="/" className="inline-flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                Amarktai
              </span>
            </Link>
            <h1 className="mt-6 text-2xl font-bold">Welcome back</h1>
            <p className="text-gray-600 mt-2">Sign in to your account to continue</p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border p-6">
            {isValidClerkKey ? (
              <SignIn 
                routing="path"
                path="/login"
                signUpUrl="/register"
                redirectUrl="/dashboard"
                appearance={{
                  elements: {
                    formButtonPrimary: 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700',
                    footerActionLink: 'text-violet-600 hover:text-violet-700',
                  }
                }}
              />
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="text-sm text-amber-800 text-center">
                    <strong>Demo Mode:</strong> No authentication required. Click below to explore the dashboard.
                  </p>
                </div>
                <Button 
                  onClick={handleDemoLogin}
                  className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
                  size="lg"
                >
                  <User className="w-4 h-4 mr-2" />
                  Enter Demo Mode
                </Button>
              </div>
            )}
          </div>
          
          <p className="text-center mt-6 text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-violet-600 hover:text-violet-700 font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
