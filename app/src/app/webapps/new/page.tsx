import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { webAppApi } from '@/lib/api';
import { toast } from 'sonner';

const categories = [
  'SaaS',
  'E-commerce',
  'Developer Tools',
  'Productivity',
  'Finance',
  'Health & Fitness',
  'Education',
  'Entertainment',
  'Other',
];

export default function NewWebAppPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    description: '',
    category: '',
    targetAudience: '',
    keyFeatures: [''] as string[],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await webAppApi.create({
        ...formData,
        keyFeatures: formData.keyFeatures.filter(f => f.trim() !== ''),
        isActive: true,
      });
      toast.success('Web app added successfully');
      navigate('/dashboard/webapps');
    } catch (error) {
      toast.error('Failed to add web app');
    } finally {
      setLoading(false);
    }
  };

  const addFeature = () => {
    setFormData({ ...formData, keyFeatures: [...formData.keyFeatures, ''] });
  };

  const removeFeature = (index: number) => {
    setFormData({
      ...formData,
      keyFeatures: formData.keyFeatures.filter((_, i) => i !== index),
    });
  };

  const updateFeature = (index: number, value: string) => {
    const newFeatures = [...formData.keyFeatures];
    newFeatures[index] = value;
    setFormData({ ...formData, keyFeatures: newFeatures });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Button 
        variant="ghost" 
        className="mb-4"
        onClick={() => navigate('/dashboard/webapps')}
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Web Apps
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Add New Web App</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">App Name *</Label>
              <Input
                id="name"
                placeholder="e.g., TaskFlow Pro"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="url">Website URL *</Label>
              <Input
                id="url"
                type="url"
                placeholder="https://yourapp.com"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="What does your app do? What problem does it solve?"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                required
              />
            </div>

            <div className="space-y-2">
              <Label>Category *</Label>
              <div className="flex flex-wrap gap-2">
                {categories.map((cat) => (
                  <Badge
                    key={cat}
                    variant={formData.category === cat ? 'default' : 'outline'}
                    className={`cursor-pointer ${
                      formData.category === cat 
                        ? 'bg-violet-600 hover:bg-violet-700' 
                        : 'hover:bg-gray-100'
                    }`}
                    onClick={() => setFormData({ ...formData, category: cat })}
                  >
                    {cat}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="targetAudience">Target Audience *</Label>
              <Input
                id="targetAudience"
                placeholder="e.g., Remote teams, project managers, startups"
                value={formData.targetAudience}
                onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label>Key Features</Label>
              <p className="text-sm text-gray-500 mb-2">
                Add features that make your app stand out. These help our AI create better content.
              </p>
              <div className="space-y-2">
                {formData.keyFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Input
                      placeholder={`Feature ${index + 1}`}
                      value={feature}
                      onChange={(e) => updateFeature(index, e.target.value)}
                    />
                    {formData.keyFeatures.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFeature(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addFeature}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Feature
              </Button>
            </div>

            <div className="flex items-center justify-end space-x-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/dashboard/webapps')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-violet-600 to-indigo-600"
                disabled={loading}
              >
                {loading ? 'Adding...' : 'Add Web App'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
