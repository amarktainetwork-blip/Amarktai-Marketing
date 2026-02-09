import { useEffect, useState } from 'react';
import { Eye, Heart, MessageCircle, Share2, MousePointer, Calendar, Search, Wand2, BarChart3, Target, Repeat } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import type { Content } from '@/types';
import { contentApi } from '@/lib/api';
import { format } from 'date-fns';
import { ContentStudio } from '@/components/dashboard/ContentStudio';
import { CompetitorIntel } from '@/components/dashboard/CompetitorIntel';
import { ContentRepurposer } from '@/components/dashboard/ContentRepurposer';

const platformIcons: Record<string, string> = {
  youtube: '▶️',
  tiktok: '🎵',
  instagram: '📷',
  facebook: '👥',
  twitter: '🐦',
  linkedin: '💼',
};

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-blue-100 text-blue-700',
  posted: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  failed: 'bg-gray-100 text-gray-700',
};

export default function ContentPage() {
  const [content, setContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      const data = await contentApi.getAll();
      setContent(data);
    } catch (error) {
      console.error('Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  const filteredContent = content.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.caption.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTab = activeTab === 'all' || item.status === activeTab;
    return matchesSearch && matchesTab;
  });

  const contentByStatus = {
    all: content.length,
    pending: content.filter(c => c.status === 'pending').length,
    approved: content.filter(c => c.status === 'approved').length,
    posted: content.filter(c => c.status === 'posted').length,
    rejected: content.filter(c => c.status === 'rejected').length,
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 bg-gray-200 rounded w-48" />
        <div className="grid gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Content Studio</h2>
          <p className="text-gray-500">Create, manage, and optimize your content</p>
        </div>
        <Button className="bg-gradient-to-r from-violet-600 to-indigo-600">
          <Wand2 className="w-4 h-4 mr-2" />
          Create New
        </Button>
      </div>

      {/* Main Tabs */}
      <Tabs defaultValue="library" className="w-full">
        <TabsList className="grid grid-cols-5 w-full max-w-3xl">
          <TabsTrigger value="library">
            <BarChart3 className="w-4 h-4 mr-2" />
            Library
          </TabsTrigger>
          <TabsTrigger value="studio">
            <Wand2 className="w-4 h-4 mr-2" />
            AI Studio
          </TabsTrigger>
          <TabsTrigger value="repurposer">
            <Repeat className="w-4 h-4 mr-2" />
            Repurposer
          </TabsTrigger>
          <TabsTrigger value="intel">
            <Target className="w-4 h-4 mr-2" />
            Intelligence
          </TabsTrigger>
          <TabsTrigger value="calendar">
            <Calendar className="w-4 h-4 mr-2" />
            Calendar
          </TabsTrigger>
        </TabsList>

        <TabsContent value="library" className="space-y-6">
          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Content Status Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-5 w-full max-w-2xl">
          <TabsTrigger value="all">
            All ({contentByStatus.all})
          </TabsTrigger>
          <TabsTrigger value="pending">
            Pending ({contentByStatus.pending})
          </TabsTrigger>
          <TabsTrigger value="approved">
            Approved ({contentByStatus.approved})
          </TabsTrigger>
          <TabsTrigger value="posted">
            Posted ({contentByStatus.posted})
          </TabsTrigger>
          <TabsTrigger value="rejected">
            Rejected ({contentByStatus.rejected})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-6">
          {filteredContent.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <p className="text-gray-500">No content found</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredContent.map((item) => (
                <Card key={item.id}>
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-start gap-4">
                      {/* Media Preview */}
                      <div className="w-full lg:w-48 h-32 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                        {item.mediaUrls[0] ? (
                          <img 
                            src={item.mediaUrls[0]} 
                            alt={item.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-400">
                            <span className="text-4xl">{platformIcons[item.platform]}</span>
                          </div>
                        )}
                      </div>

                      {/* Content Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-lg">{platformIcons[item.platform]}</span>
                          <Badge variant="outline" className="capitalize">
                            {item.platform}
                          </Badge>
                          <Badge className={statusColors[item.status]}>
                            {item.status}
                          </Badge>
                          <Badge variant="outline" className="capitalize">
                            {item.type}
                          </Badge>
                        </div>

                        <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
                        <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                          {item.caption}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-3">
                          {item.hashtags.map((tag, i) => (
                            <span key={i} className="text-xs text-violet-600 bg-violet-50 px-2 py-1 rounded">
                              #{tag}
                            </span>
                          ))}
                        </div>

                        <div className="flex items-center text-sm text-gray-500 space-x-4">
                          <span className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            {format(new Date(item.createdAt), 'MMM d, yyyy')}
                          </span>
                          {item.scheduledFor && (
                            <span className="flex items-center">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2" />
                              Scheduled for {format(new Date(item.scheduledFor), 'MMM d, h:mm a')}
                            </span>
                          )}
                          {item.postedAt && (
                            <span className="flex items-center text-green-600">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                              Posted on {format(new Date(item.postedAt), 'MMM d')}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Performance Stats */}
                      {item.performance && (
                        <div className="flex flex-wrap lg:flex-col gap-3 lg:w-32">
                          <div className="flex items-center text-sm">
                            <Eye className="w-4 h-4 mr-1 text-gray-400" />
                            <span>{item.performance.views.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center text-sm">
                            <Heart className="w-4 h-4 mr-1 text-pink-400" />
                            <span>{item.performance.likes.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center text-sm">
                            <MessageCircle className="w-4 h-4 mr-1 text-blue-400" />
                            <span>{item.performance.comments.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center text-sm">
                            <Share2 className="w-4 h-4 mr-1 text-green-400" />
                            <span>{item.performance.shares.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center text-sm">
                            <MousePointer className="w-4 h-4 mr-1 text-violet-400" />
                            <span>{item.performance.ctr}% CTR</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
        </TabsContent>

        <TabsContent value="studio">
          <ContentStudio />
        </TabsContent>

        <TabsContent value="repurposer">
          <ContentRepurposer />
        </TabsContent>

        <TabsContent value="intel">
          <CompetitorIntel />
        </TabsContent>

        <TabsContent value="calendar">
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-300 mb-2">Content Calendar</h3>
            <p className="text-slate-500">View your scheduled content in calendar format</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
