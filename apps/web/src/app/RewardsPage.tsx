import React, { useState, useEffect } from 'react';
import { Trophy, Award, Star, Target, TrendingUp, Gift } from 'lucide-react';

interface Reward {
  id: string;
  type: 'badge' | 'points' | 'bonus';
  name: string;
  description: string;
  value: number;
  earnedAt: string;
  source: 'manual' | 'ai_auto' | 'ai_suggested';
  awardedBy?: string;
}

interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  points: number;
  earned: boolean;
  earnedAt?: string;
  progress?: number;
}

const RewardsPage: React.FC = () => {
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [totalPoints, setTotalPoints] = useState(0);
  const [aiSuggestions, setAiSuggestions] = useState([]);

  useEffect(() => {
    fetchRewardsData();
  }, []);

  const fetchRewardsData = async () => {
    // Fetch from API
    const data = await fetch('/api/rewards/my-rewards').then(r => r.json());
    setRewards(data.rewards);
    setBadges(data.badges);
    setTotalPoints(data.total_points);
    setAiSuggestions(data.ai_suggestions);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Rewards & Achievements
        </h1>
        <p className="text-gray-600">
          Track your progress, earn badges, and celebrate wins! 🎉
        </p>
      </div>

      {/* Points Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Star className="w-8 h-8" />
            <h3 className="text-xl font-semibold">Total Points</h3>
          </div>
          <p className="text-4xl font-bold">{totalPoints.toLocaleString()}</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Trophy className="w-8 h-8" />
            <h3 className="text-xl font-semibold">Badges Earned</h3>
          </div>
          <p className="text-4xl font-bold">
            {badges.filter(b => b.earned).length}
          </p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Gift className="w-8 h-8" />
            <h3 className="text-xl font-semibold">Rewards</h3>
          </div>
          <p className="text-4xl font-bold">{rewards.length}</p>
        </div>
      </div>

      {/* AI Suggestions */}
      {aiSuggestions.length > 0 && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 rounded-xl p-6 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-6 h-6 text-amber-600" />
            <h2 className="text-2xl font-bold text-gray-900">
              AI Detected Achievements! 🤖
            </h2>
          </div>
          <p className="text-gray-600 mb-4">
            Our AI noticed some great work. These rewards are pending manager approval:
          </p>
          <div className="space-y-3">
            {aiSuggestions.map((suggestion: any) => (
              <div key={suggestion.id} className="bg-white rounded-lg p-4 border border-amber-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {suggestion.reward_name}
                    </h3>
                    <p className="text-sm text-gray-600">{suggestion.reasoning}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      AI Confidence: {(suggestion.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-amber-600">
                      {suggestion.value} pts
                    </p>
                    <p className="text-xs text-gray-500">Pending Approval</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Badge Collection */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Badge Collection</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {badges.map((badge) => (
            <div
              key={badge.id}
              className={`relative p-4 rounded-lg text-center transition-all ${
                badge.earned
                  ? 'bg-gradient-to-br from-yellow-100 to-yellow-200 border-2 border-yellow-300 shadow-md'
                  : 'bg-gray-100 border-2 border-gray-200 opacity-50'
              }`}
            >
              <div className="text-5xl mb-2">{badge.icon}</div>
              <h3 className="font-semibold text-sm text-gray-900 mb-1">
                {badge.name}
              </h3>
              <p className="text-xs text-gray-600 mb-2">{badge.description}</p>
              <p className="text-sm font-bold text-blue-600">
                {badge.points} pts
              </p>
              {badge.earned && (
                <div className="absolute top-2 right-2">
                  <div className="bg-green-500 rounded-full p-1">
                    <Award className="w-3 h-3 text-white" />
                  </div>
                </div>
              )}
              {!badge.earned && badge.progress !== undefined && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${badge.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {badge.progress}% complete
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Rewards */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Rewards</h2>
        <div className="space-y-3">
          {rewards.map((reward) => (
            <div
              key={reward.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-full ${
                  reward.type === 'badge' ? 'bg-purple-100' :
                  reward.type === 'points' ? 'bg-blue-100' :
                  'bg-green-100'
                }`}>
                  {reward.type === 'badge' && <Trophy className="w-6 h-6 text-purple-600" />}
                  {reward.type === 'points' && <Star className="w-6 h-6 text-blue-600" />}
                  {reward.type === 'bonus' && <Gift className="w-6 h-6 text-green-600" />}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{reward.name}</h3>
                  <p className="text-sm text-gray-600">{reward.description}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-xs text-gray-500">
                      {new Date(reward.earnedAt).toLocaleDateString()}
                    </p>
                    {reward.source === 'ai_auto' && (
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                        AI Auto-Awarded
                      </span>
                    )}
                    {reward.source === 'manual' && reward.awardedBy && (
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                        Awarded by Manager
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">
                  {reward.type === 'bonus' ? `$${reward.value}` : `${reward.value} pts`}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RewardsPage;
