import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Zap, Gallery, Users, TrendingUp } from 'lucide-react';
import { statsAPI } from '../services/api';

const HomePage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await statsAPI.get();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const features = [
    {
      title: "Create Avatars",
      description: "Upload 5-20 facial images to train personalized DreamBooth models",
      icon: Users,
      link: "/create-avatar",
      color: "bg-primary"
    },
    {
      title: "Generate Images",
      description: "Create stunning images using your trained avatar models",
      icon: Zap,
      link: "/generate",
      color: "bg-secondary"
    },
    {
      title: "View Gallery",
      description: "Browse and manage your generated content",
      icon: Gallery,
      link: "/gallery",
      color: "bg-accent"
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="hero min-h-[60vh] bg-gradient-to-br from-primary/20 to-secondary/20 rounded-3xl mb-12">
        <div className="hero-content text-center">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold mb-6">
              Avatar Engine
            </h1>
            <p className="text-xl mb-8 opacity-80">
              Create personalized AI avatars with DreamBooth training and generate stunning images & videos
            </p>
            <div className="flex gap-4 justify-center">
              <Link to="/create-avatar" className="btn btn-primary btn-lg">
                <Plus className="w-5 h-5 mr-2" />
                Create Avatar
              </Link>
              <Link to="/generate" className="btn btn-outline btn-lg">
                <Zap className="w-5 h-5 mr-2" />
                Generate
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      {!loading && stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="stat bg-base-200 rounded-2xl">
            <div className="stat-figure text-primary">
              <Users className="w-8 h-8" />
            </div>
            <div className="stat-title">Total Avatars</div>
            <div className="stat-value text-primary">
              {Object.values(stats.avatar_counts || {}).reduce((a, b) => a + b, 0)}
            </div>
          </div>
          
          <div className="stat bg-base-200 rounded-2xl">
            <div className="stat-figure text-secondary">
              <TrendingUp className="w-8 h-8" />
            </div>
            <div className="stat-title">Total Generations</div>
            <div className="stat-value text-secondary">{stats.total_generations || 0}</div>
          </div>
          
          <div className="stat bg-base-200 rounded-2xl">
            <div className="stat-figure text-accent">
              <Zap className="w-8 h-8" />
            </div>
            <div className="stat-title">Recent (24h)</div>
            <div className="stat-value text-accent">{stats.recent_generations || 0}</div>
          </div>
          
          <div className="stat bg-base-200 rounded-2xl">
            <div className="stat-figure text-success">
              <Gallery className="w-8 h-8" />
            </div>
            <div className="stat-title">Storage Used</div>
            <div className="stat-value text-success">
              {((stats.storage_used?.avatars_mb || 0) + 
                (stats.storage_used?.outputs_mb || 0)).toFixed(1)}MB
            </div>
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        {features.map((feature, index) => (
          <Link
            key={index}
            to={feature.link}
            className="card bg-base-200 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105"
          >
            <div className="card-body items-center text-center">
              <div className={`w-16 h-16 rounded-full ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h2 className="card-title text-2xl mb-2">{feature.title}</h2>
              <p className="opacity-70">{feature.description}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Features List */}
      <div className="card bg-base-200 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-3xl mb-6">✨ Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                <div>
                  <h3 className="font-semibold">DreamBooth Training</h3>
                  <p className="text-sm opacity-70">Upload 5-20 images to train personalized LoRA models</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-secondary rounded-full mt-2"></div>
                <div>
                  <h3 className="font-semibold">ComfyUI Integration</h3>
                  <p className="text-sm opacity-70">Powerful image and video generation pipeline</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-accent rounded-full mt-2"></div>
                <div>
                  <h3 className="font-semibold">NSFW Support</h3>
                  <p className="text-sm opacity-70">Optional uncensored content generation</p>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-success rounded-full mt-2"></div>
                <div>
                  <h3 className="font-semibold">Video Generation</h3>
                  <p className="text-sm opacity-70">AnimateDiff integration for video creation</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-warning rounded-full mt-2"></div>
                <div>
                  <h3 className="font-semibold">Privacy First</h3>
                  <p className="text-sm opacity-70">Local deployment, no telemetry or filtering</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-error rounded-full mt-2"></div>
                <div>
                  <h3 className="font-semibold">RunPod Compatible</h3>
                  <p className="text-sm opacity-70">Scale training with cloud GPU instances</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;