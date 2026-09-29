import MetricsCard from './MetricsCard';
import ImagePreview from './ImagePreview';
import MatchAnalytics from './MatchAnalytics';
import { Activity, Target, Clock } from 'lucide-react';

export const ResultPanel = ({ results }) => {
  if (!results) return null;

  const { match_image, aligned_image, rmse, inlier_ratio, compute_time, match_details } = results;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricsCard
          title="Root Mean Square Error"
          value={typeof rmse === 'number' ? rmse.toFixed(4) : rmse}
          unit="px"
          icon={Activity}
          description="Geometric misalignment error magnitude"
        />
        <MetricsCard
          title="Inlier Matching Ratio"
          value={typeof inlier_ratio === 'number' ? `${(inlier_ratio * 100).toFixed(1)}%` : inlier_ratio}
          icon={Target}
          description="Robust feature point consensus ratio"
        />
        <MetricsCard
          title="Processing Duration"
          value={typeof compute_time === 'number' ? compute_time.toFixed(3) : compute_time}
          unit="sec"
          icon={Clock}
          description="Server compute pipeline latency"
        />
      </div>

      {/* Visual Alignment Outputs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ImagePreview
          title="Feature Keypoint Matching Map"
          base64String={match_image}
          badge="Correspondence"
          filename="luna_match_features.png"
        />
        <ImagePreview
          title="Final Aligned Surface Output"
          base64String={aligned_image}
          badge="Registered"
          filename="luna_aligned_surface.png"
        />
      </div>

      <MatchAnalytics details={match_details} />
    </div>
  );
};

export default ResultPanel;