import React, { useState, useEffect } from 'react';
import { Gallery, Image, Video, Download, ExternalLink } from 'lucide-react';

const GalleryPage = () => {
  const [generations, setGenerations] = useState([]);
  const [filter, setFilter] = useState('all'); // all, image, video
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // This would fetch generation history from the API
    // For now, we'll show a placeholder
    setLoading(false);
  }, []);

  const mockGenerations = [
    {
      id: '1',
      type: 'image',
      avatar_token: 'avtr_12345678',
      prompt: 'avtr_12345678 person, portrait, professional photo',
      output_url: '/placeholder-image.jpg',
      created_at: new Date().toISOString(),
      status: 'completed'
    },
    {
      id: '2',
      type: 'video',
      avatar_token: 'avtr_87654321',
      prompt: 'avtr_87654321 person, walking, outdoor scene',
      output_url: '/placeholder-video.mp4',
      created_at: new Date().toISOString(),
      status: 'completed'
    }
  ];

  const filteredGenerations = filter === 'all' 
    ? mockGenerations 
    : mockGenerations.filter(gen => gen.type === filter);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Gallery</h1>
        <p className="text-lg opacity-70">
          Browse and manage your generated content
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="tabs tabs-boxed mb-8 bg-base-200">
        <button
          className={`tab ${filter === 'all' ? 'tab-active' : ''}`}
          onClick={() => setFilter('all')}
        >
          <Gallery className="w-4 h-4 mr-2" />
          All ({mockGenerations.length})
        </button>
        <button
          className={`tab ${filter === 'image' ? 'tab-active' : ''}`}
          onClick={() => setFilter('image')}
        >
          <Image className="w-4 h-4 mr-2" />
          Images ({mockGenerations.filter(g => g.type === 'image').length})
        </button>
        <button
          className={`tab ${filter === 'video' ? 'tab-active' : ''}`}
          onClick={() => setFilter('video')}
        >
          <Video className="w-4 h-4 mr-2" />
          Videos ({mockGenerations.filter(g => g.type === 'video').length})
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center min-h-[50vh]">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : filteredGenerations.length === 0 ? (
        <div className="text-center py-16">
          <Gallery className="w-24 h-24 mx-auto mb-6 opacity-30" />
          <h2 className="text-3xl font-bold mb-4">No Generations Yet</h2>
          <p className="text-lg opacity-70 mb-8">
            Generate some content to see it here
          </p>
          <a href="/generate" className="btn btn-primary btn-lg">
            Start Generating
          </a>
        </div>
      ) : (
        <div className="image-grid">
          {filteredGenerations.map((generation) => (
            <div key={generation.id} className="generation-card card bg-base-200 shadow-xl">
              <figure className="aspect-square bg-base-300">
                {generation.type === 'image' ? (
                  <div className="w-full h-full flex items-center justify-center">
                    <Image className="w-16 h-16 opacity-30" />
                    <span className="ml-2 opacity-50">Image Preview</span>
                  </div>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Video className="w-16 h-16 opacity-30" />
                    <span className="ml-2 opacity-50">Video Preview</span>
                  </div>
                )}
              </figure>
              
              <div className="card-body p-4">
                <div className="flex items-center gap-2 mb-2">
                  {generation.type === 'image' ? (
                    <Image className="w-4 h-4" />
                  ) : (
                    <Video className="w-4 h-4" />
                  )}
                  <span className="badge badge-primary">{generation.avatar_token}</span>
                </div>
                
                <p className="text-sm opacity-70 line-clamp-2 mb-3">
                  {generation.prompt}
                </p>
                
                <div className="text-xs opacity-50 mb-3">
                  {new Date(generation.created_at).toLocaleDateString()}
                </div>
                
                <div className="card-actions justify-between">
                  <button className="btn btn-sm btn-outline">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="btn btn-sm btn-primary">
                    <ExternalLink className="w-4 h-4" />
                    View
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Placeholder message */}
      <div className="alert alert-info mt-8">
        <div>
          <div className="font-semibold">Gallery Coming Soon</div>
          <div>The gallery will display your generated images and videos once the backend integration is complete.</div>
        </div>
      </div>
    </div>
  );
};

export default GalleryPage;