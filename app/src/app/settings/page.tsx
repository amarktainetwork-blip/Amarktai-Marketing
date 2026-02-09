import { useState } from 'react';
import { Bell, Clock, Shield, User, CreditCard } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    emailDaily: true,
    emailWeekly: true,
    pushApproval: true,
    pushPosted: false,
  });

  const [preferences, setPreferences] = useState({
    postingTime: '10:00',
    timezone: 'America/New_York',
    language: 'en',
  });

  const handleSaveNotifications = () => {
    toast.success('Notification preferences saved');
  };

  const handleSavePreferences = () => {
    toast.success('Preferences saved');
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-gray-500">Manage your account and preferences</p>
      </div>

      {/* Plan Info */}
      <Card className="bg-gradient-to-r from-violet-50 to-indigo-50 border-violet-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-violet-600 font-medium">Current Plan</p>
              <h3 className="text-2xl font-bold text-violet-900">Pro</h3>
              <p className="text-violet-700 text-sm mt-1">
                $29/month • Renews on March 15, 2024
              </p>
            </div>
            <Button variant="outline" className="bg-white">
              <CreditCard className="w-4 h-4 mr-2" />
              Manage Subscription
            </Button>
          </div>
          <div className="mt-4 pt-4 border-t border-violet-200">
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="bg-white">5 Web Apps</Badge>
              <Badge variant="outline" className="bg-white">6 Platforms</Badge>
              <Badge variant="outline" className="bg-white">12 posts/day</Badge>
              <Badge variant="outline" className="bg-white">Priority Support</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="w-5 h-5 mr-2" />
            Notifications
          </CardTitle>
          <CardDescription>
            Choose how you want to be notified
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <h4 className="font-medium text-sm text-gray-500 uppercase tracking-wide">Email Notifications</h4>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="email-daily" className="font-medium">Daily Content Ready</Label>
                <p className="text-sm text-gray-500">Get an email when new content is generated</p>
              </div>
              <Switch
                id="email-daily"
                checked={notifications.emailDaily}
                onCheckedChange={(checked) => setNotifications({ ...notifications, emailDaily: checked })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="email-weekly" className="font-medium">Weekly Analytics</Label>
                <p className="text-sm text-gray-500">Receive weekly performance summary</p>
              </div>
              <Switch
                id="email-weekly"
                checked={notifications.emailWeekly}
                onCheckedChange={(checked) => setNotifications({ ...notifications, emailWeekly: checked })}
              />
            </div>
          </div>

          <div className="border-t pt-4 space-y-4">
            <h4 className="font-medium text-sm text-gray-500 uppercase tracking-wide">Push Notifications</h4>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="push-approval" className="font-medium">Content Approval</Label>
                <p className="text-sm text-gray-500">Notify when content is ready for approval</p>
              </div>
              <Switch
                id="push-approval"
                checked={notifications.pushApproval}
                onCheckedChange={(checked) => setNotifications({ ...notifications, pushApproval: checked })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="push-posted" className="font-medium">Content Posted</Label>
                <p className="text-sm text-gray-500">Notify when content goes live</p>
              </div>
              <Switch
                id="push-posted"
                checked={notifications.pushPosted}
                onCheckedChange={(checked) => setNotifications({ ...notifications, pushPosted: checked })}
              />
            </div>
          </div>

          <Button onClick={handleSaveNotifications} className="bg-gradient-to-r from-violet-600 to-indigo-600">
            Save Notification Settings
          </Button>
        </CardContent>
      </Card>

      {/* Posting Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Posting Preferences
          </CardTitle>
          <CardDescription>
            Configure when and how your content is posted
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="posting-time">Preferred Posting Time</Label>
              <Input
                id="posting-time"
                type="time"
                value={preferences.postingTime}
                onChange={(e) => setPreferences({ ...preferences, postingTime: e.target.value })}
              />
              <p className="text-sm text-gray-500">Content will be posted around this time</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <select
                id="timezone"
                value={preferences.timezone}
                onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/Denver">Mountain Time (MT)</option>
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="Europe/London">London (GMT)</option>
                <option value="Europe/Paris">Paris (CET)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
                <option value="Australia/Sydney">Sydney (AEST)</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>AI Generation Schedule</Label>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Daily at 2:00 AM</p>
                  <p className="text-sm text-gray-500">Content is generated automatically</p>
                </div>
                <Badge variant="outline">Active</Badge>
              </div>
            </div>
          </div>

          <Button onClick={handleSavePreferences} className="bg-gradient-to-r from-violet-600 to-indigo-600">
            Save Preferences
          </Button>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="w-5 h-5 mr-2" />
            Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-gray-500">Add an extra layer of security</p>
            </div>
            <Button variant="outline">Enable</Button>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Change Password</p>
              <p className="text-sm text-gray-500">Last changed 30 days ago</p>
            </div>
            <Button variant="outline">Change</Button>
          </div>
        </CardContent>
      </Card>

      {/* Connected Accounts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="w-5 h-5 mr-2" />
            Connected Accounts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-semibold mr-3">
                JD
              </div>
              <div>
                <p className="font-medium">john.doe@example.com</p>
                <p className="text-sm text-gray-500">Clerk Account</p>
              </div>
            </div>
            <Badge>Connected</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
