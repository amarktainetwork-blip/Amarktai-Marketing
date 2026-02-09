import { SmartScheduler } from '@/components/dashboard/SmartScheduler';

export default function SchedulerPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Smart Scheduler</h2>
        <p className="text-gray-500">
          AI-powered scheduling to maximize engagement and reach
        </p>
      </div>
      
      <SmartScheduler />
    </div>
  );
}
