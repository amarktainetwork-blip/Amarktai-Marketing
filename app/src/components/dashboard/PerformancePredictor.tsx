import { useState } from 'react';
import { TrendingUp, Eye, Heart, MousePointer, AlertTriangle, CheckCircle, Lightbulb } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface PredictionResult {
  predicted_views: number;
  predicted_engagement: number;
  predicted_ctr: number;
  confidence_score: number;
  risk_level: 'low' | 'medium' | 'high';
  improvement_suggestions: string[];
}

interface PerformancePredictorProps {
  content?: {
    caption: string;
    hashtags: string[];
    platform: string;
  };
}

export default function PerformancePredictor({ content: _content }: PerformancePredictorProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);

  // Mock prediction function
  const analyzeContent = () => {
    setIsAnalyzing(true);
    
    // Simulate API call
    setTimeout(() => {
      const mockPrediction: PredictionResult = {
        predicted_views: 2500,
        predicted_engagement: 180,
        predicted_ctr: 8.5,
        confidence_score: 0.82,
        risk_level: 'low',
        improvement_suggestions: [
          '💡 Add a stronger hook in the first sentence',
          '💡 Use 5-8 hashtags for optimal reach',
          '💡 Post at 2 PM for maximum engagement'
        ]
      };
      
      setPrediction(mockPrediction);
      setIsAnalyzing(false);
    }, 1500);
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'low': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'high': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default: return null;
    }
  };

  if (!prediction) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center text-lg">
            <TrendingUp className="w-5 h-5 mr-2 text-violet-600" />
            AI Performance Predictor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-violet-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-violet-600" />
            </div>
            <h3 className="font-semibold mb-2">Predict Your Content Performance</h3>
            <p className="text-gray-500 text-sm mb-4 max-w-sm mx-auto">
              Our AI analyzes your content and predicts views, engagement, and CTR before you post.
            </p>
            <button
              onClick={analyzeContent}
              disabled={isAnalyzing}
              className="px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:from-violet-700 hover:to-indigo-700 disabled:opacity-50"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Content'}
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg">
            <TrendingUp className="w-5 h-5 mr-2 text-violet-600" />
            Performance Prediction
          </CardTitle>
          <Badge className={getRiskColor(prediction.risk_level)}>
            {getRiskIcon(prediction.risk_level)}
            <span className="ml-1 capitalize">{prediction.risk_level} Risk</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Confidence Score */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-500">AI Confidence</span>
            <span className="font-medium">{Math.round(prediction.confidence_score * 100)}%</span>
          </div>
          <Progress value={prediction.confidence_score * 100} className="h-2" />
        </div>

        {/* Predictions */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <Eye className="w-5 h-5 text-blue-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-blue-700">
              {prediction.predicted_views >= 1000 
                ? `${(prediction.predicted_views / 1000).toFixed(1)}K` 
                : prediction.predicted_views}
            </p>
            <p className="text-xs text-blue-600">Predicted Views</p>
          </div>
          <div className="text-center p-3 bg-pink-50 rounded-lg">
            <Heart className="w-5 h-5 text-pink-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-pink-700">
              {prediction.predicted_engagement >= 1000 
                ? `${(prediction.predicted_engagement / 1000).toFixed(1)}K` 
                : prediction.predicted_engagement}
            </p>
            <p className="text-xs text-pink-600">Engagement</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <MousePointer className="w-5 h-5 text-green-600 mx-auto mb-1" />
            <p className="text-2xl font-bold text-green-700">{prediction.predicted_ctr}%</p>
            <p className="text-xs text-green-600">Predicted CTR</p>
          </div>
        </div>

        {/* Improvement Suggestions */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <div className="flex items-center mb-2">
            <Lightbulb className="w-4 h-4 text-amber-600 mr-2" />
            <span className="text-sm font-medium text-amber-800">Improvement Suggestions</span>
          </div>
          <ul className="space-y-1">
            {prediction.improvement_suggestions.map((suggestion, i) => (
              <li key={i} className="text-sm text-amber-700 flex items-start">
                <span className="mr-2">•</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>

        {/* Re-analyze button */}
        <button
          onClick={() => setPrediction(null)}
          className="w-full py-2 text-sm text-violet-600 hover:text-violet-700 border border-violet-200 rounded-lg hover:bg-violet-50"
        >
          Analyze Different Content
        </button>
      </CardContent>
    </Card>
  );
}
