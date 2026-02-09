import type { WebApp, PlatformConnection, Content, AnalyticsSummary, Platform } from '@/types';
import { mockWebApps, mockPlatformConnections, mockContent, mockAnalytics } from './mockData';

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Web Apps API
export const webAppApi = {
  getAll: async (): Promise<WebApp[]> => {
    await delay(300);
    return [...mockWebApps];
  },

  getById: async (id: string): Promise<WebApp | null> => {
    await delay(200);
    return mockWebApps.find(app => app.id === id) || null;
  },

  create: async (data: Omit<WebApp, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<WebApp> => {
    await delay(500);
    const newApp: WebApp = {
      ...data,
      id: `webapp-${Date.now()}`,
      userId: 'user-1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    mockWebApps.push(newApp);
    return newApp;
  },

  update: async (id: string, data: Partial<WebApp>): Promise<WebApp> => {
    await delay(400);
    const index = mockWebApps.findIndex(app => app.id === id);
    if (index === -1) throw new Error('Web app not found');
    mockWebApps[index] = { ...mockWebApps[index], ...data, updatedAt: new Date().toISOString() };
    return mockWebApps[index];
  },

  delete: async (id: string): Promise<void> => {
    await delay(300);
    const index = mockWebApps.findIndex(app => app.id === id);
    if (index !== -1) mockWebApps.splice(index, 1);
  },
};

// Platform Connections API
export const platformApi = {
  getAll: async (): Promise<PlatformConnection[]> => {
    await delay(300);
    return [...mockPlatformConnections];
  },

  getByPlatform: async (platform: Platform): Promise<PlatformConnection | null> => {
    await delay(200);
    return mockPlatformConnections.find(conn => conn.platform === platform) || null;
  },

  connect: async (platform: Platform, accountName: string): Promise<PlatformConnection> => {
    await delay(1000);
    // Simulate OAuth flow
    const newConnection: PlatformConnection = {
      id: `conn-${Date.now()}`,
      userId: 'user-1',
      platform,
      accountName,
      accountId: `${platform}-${Math.random().toString(36).substr(2, 9)}`,
      isActive: true,
      connectedAt: new Date().toISOString(),
    };
    mockPlatformConnections.push(newConnection);
    return newConnection;
  },

  disconnect: async (platform: Platform): Promise<void> => {
    await delay(500);
    const index = mockPlatformConnections.findIndex(conn => conn.platform === platform);
    if (index !== -1) mockPlatformConnections.splice(index, 1);
  },
};

// Content API
export const contentApi = {
  getAll: async (status?: Content['status']): Promise<Content[]> => {
    await delay(300);
    if (status) {
      return mockContent.filter(c => c.status === status);
    }
    return [...mockContent];
  },

  getPending: async (): Promise<Content[]> => {
    await delay(300);
    return mockContent.filter(c => c.status === 'pending');
  },

  getById: async (id: string): Promise<Content | null> => {
    await delay(200);
    return mockContent.find(c => c.id === id) || null;
  },

  approve: async (id: string): Promise<Content> => {
    await delay(400);
    const index = mockContent.findIndex(c => c.id === id);
    if (index === -1) throw new Error('Content not found');
    mockContent[index] = { 
      ...mockContent[index], 
      status: 'approved',
      updatedAt: new Date().toISOString(),
    };
    return mockContent[index];
  },

  reject: async (id: string): Promise<Content> => {
    await delay(400);
    const index = mockContent.findIndex(c => c.id === id);
    if (index === -1) throw new Error('Content not found');
    mockContent[index] = { 
      ...mockContent[index], 
      status: 'rejected',
      updatedAt: new Date().toISOString(),
    };
    return mockContent[index];
  },

  approveAll: async (ids: string[]): Promise<void> => {
    await delay(600);
    ids.forEach(id => {
      const index = mockContent.findIndex(c => c.id === id);
      if (index !== -1) {
        mockContent[index] = { 
          ...mockContent[index], 
          status: 'approved',
          updatedAt: new Date().toISOString(),
        };
      }
    });
  },

  updateCaption: async (id: string, caption: string): Promise<Content> => {
    await delay(300);
    const index = mockContent.findIndex(c => c.id === id);
    if (index === -1) throw new Error('Content not found');
    mockContent[index] = { 
      ...mockContent[index], 
      caption,
      updatedAt: new Date().toISOString(),
    };
    return mockContent[index];
  },

  generate: async (webappId: string, platform: Platform): Promise<Content> => {
    await delay(2000);
    // Simulate AI content generation
    const templates: Record<Platform, Partial<Content>> = {
      youtube: {
        title: 'How to Boost Productivity with AI Tools',
        caption: 'Discover the AI tools that are transforming how teams work! 🚀\n\nIn this video, we break down the top strategies for leveraging AI in your daily workflow.\n\n#Productivity #AI #TeamWork #Innovation',
        hashtags: ['Productivity', 'AI', 'TeamWork', 'Innovation'],
      },
      tiktok: {
        title: 'POV: AI Does Your Work',
        caption: 'When AI handles the boring stuff so you can focus on what matters 😎\n\n#AITools #WorkLife #ProductivityHacks',
        hashtags: ['AITools', 'WorkLife', 'ProductivityHacks'],
      },
      instagram: {
        title: 'Morning Routine of Successful Teams',
        caption: 'The best teams start their day with these 3 habits ☀️\n\nSave this for later!\n\n#MorningRoutine #TeamSuccess #Productivity',
        hashtags: ['MorningRoutine', 'TeamSuccess', 'Productivity'],
      },
      facebook: {
        title: 'Why Smart Teams Choose AI',
        caption: 'AI isn\'t just a buzzword—it\'s a competitive advantage. Here\'s why leading teams are adopting AI tools in 2024.',
        hashtags: ['AI', 'BusinessGrowth', 'Innovation'],
      },
      twitter: {
        title: 'Quick Tip',
        caption: '💡 The teams that will win in 2024 are the ones that embrace AI not as a replacement, but as an amplifier of human creativity.\n\nWhat\'s your take on AI in the workplace?',
        hashtags: ['AI', 'FutureOfWork', 'TeamBuilding'],
      },
      linkedin: {
        title: 'The ROI of AI-Powered Teams',
        caption: 'New research shows that teams using AI tools report:\n\n✅ 40% faster project completion\n✅ 35% reduction in meeting time\n✅ 50% increase in creative output\n\nThe question isn\'t whether to adopt AI—it\'s how quickly you can integrate it into your workflow.\n\nWhat\'s your organization\'s approach to AI adoption?',
        hashtags: ['Leadership', 'AI', 'BusinessStrategy', 'Innovation'],
      },
    };

    const template = templates[platform];
    const newContent: Content = {
      id: `content-${Date.now()}`,
      userId: 'user-1',
      webappId,
      platform,
      type: platform === 'youtube' || platform === 'tiktok' ? 'video' : 'image',
      status: 'pending',
      title: template.title || 'Generated Content',
      caption: template.caption || 'Check out this amazing tool!',
      hashtags: template.hashtags || ['Innovation', 'Tech'],
      mediaUrls: [`https://images.unsplash.com/photo-${Math.random().toString(36).substr(2, 10)}?w=800`],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    mockContent.push(newContent);
    return newContent;
  },
};

// Analytics API
export const analyticsApi = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    await delay(400);
    return mockAnalytics;
  },

  getPlatformStats: async (platform: Platform): Promise<AnalyticsSummary['platformBreakdown'][Platform]> => {
    await delay(300);
    return mockAnalytics.platformBreakdown[platform];
  },
};
