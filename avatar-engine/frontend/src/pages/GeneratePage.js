import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Zap, Image, Video, Settings } from 'lucide-react';
import toast from 'react-hot-toast';
import { avatarAPI, generationAPI } from '../services/api';

const GeneratePage = () => {
  const [searchParams] = useSearchParams();
  const [avatars, setAvatars] = useState([]);
  const [selectedAvatar, setSelectedAvatar] = useState(searchParams.get('avatar') || '');
  const [generationType, setGenerationType] = useState('image');
  const [generating, setGenerating] = useState(false);
  
  // Form state
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [steps, setSteps] = useState(20);
  const [cfgScale, setCfgScale] = useState(7.0);
  const [width, setWidth] = useState(512);
  const [height, setHeight] = useState(512);
  const [seed, setSeed] = useState('');
  const [nsfw, setNsfw] = useState(false);
  
  // Video specific
  const [frames, setFrames] = useState(16);
  const [fps, setFps] = useState(8);

  useEffect(() => {
    fetchAvatars();
  }, []);

  const fetchAvatars = async () => {
    try {
      const data = await avatarAPI.list();
      const trainedAvatars = (data.avatars || []).filter(avatar => avatar.status === 'trained');
      setAvatars(trainedAvatars);
      
      if (!selectedAvatar && trainedAvatars.length > 0) {
        setSelectedAvatar(trainedAvatars[0].token);
      }
    } catch (error) {
      console.error('Failed to fetch avatars:', error);
      toast.error('Failed to load avatars');
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    if (!selectedAvatar) {
      toast.error('Please select an avatar');
      return;
    }
    
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setGenerating(true);
    
    try {
      const request = {
        avatar_token: selectedAvatar,
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim() || undefined,
        steps,
        cfg_scale: cfgScale,
        seed: seed ? parseInt(seed) : undefined,
        nsfw
      };

      let result;
      if (generationType === 'image') {
        result = await generationAPI.generateImage({
          ...request,
          width,
          height
        });
      } else {
        result = await generationAPI.generateVideo({
          ...request,
          frames,
          fps
        });
      }
      
      toast.success(`${generationType} generation started! Check the gallery for results.`);
      
      // Reset form
      setPrompt('');
      setNegativePrompt('');
      setSeed('');
      
    } catch (error) {
      console.error('Generation failed:', error);
      toast.error(error.response?.data?.detail || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const selectedAvatarData = avatars.find(a => a.token === selectedAvatar);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Generate Content</h1>
        <p className="text-lg opacity-70">
          Create images and videos using your trained avatar models
        </p>
      </div>

      {avatars.length === 0 ? (
        <div className="text-center py-16">
          <Zap className="w-24 h-24 mx-auto mb-6 opacity-30" />
          <h2 className="text-3xl font-bold mb-4">No Trained Avatars</h2>
          <p className="text-lg opacity-70 mb-8">
            You need at least one trained avatar to generate content
          </p>
          <a href="/create-avatar" className="btn btn-primary btn-lg">
            Create Your First Avatar
          </a>
        </div>
      ) : (
        <form onSubmit={handleGenerate} className="space-y-8">
          {/* Avatar Selection */}
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">
                <Settings className="w-6 h-6" />
                Generation Settings
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text text-lg">Avatar</span>
                  </label>
                  <select
                    className="select select-bordered select-lg"
                    value={selectedAvatar}
                    onChange={(e) => setSelectedAvatar(e.target.value)}
                    required
                  >
                    <option value="">Select an avatar</option>
                    {avatars.map(avatar => (
                      <option key={avatar.token} value={avatar.token}>
                        {avatar.name} ({avatar.token})
                      </option>
                    ))}
                  </select>
                  {selectedAvatarData && (
                    <label className="label">
                      <span className="label-text-alt">
                        Token: {selectedAvatarData.token} • Images: {selectedAvatarData.training_images_count}
                      </span>
                    </label>
                  )}
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text text-lg">Generation Type</span>
                  </label>
                  <div className="btn-group">
                    <button
                      type="button"
                      className={`btn ${generationType === 'image' ? 'btn-active' : ''}`}
                      onClick={() => setGenerationType('image')}
                    >
                      <Image className="w-4 h-4 mr-2" />
                      Image
                    </button>
                    <button
                      type="button"
                      className={`btn ${generationType === 'video' ? 'btn-active' : ''}`}
                      onClick={() => setGenerationType('video')}
                    >
                      <Video className="w-4 h-4 mr-2" />
                      Video
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Prompt Section */}
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">Prompt</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text text-lg">Positive Prompt *</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-32 text-base"
                  placeholder={`${selectedAvatarData?.token || '[avatar_token]'} person, portrait, high quality, detailed...`}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  required
                />
                <label className="label">
                  <span className="label-text-alt">
                    Include "{selectedAvatarData?.token || '[avatar_token]'} person" in your prompt to use the avatar
                  </span>
                </label>
              </div>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text text-lg">Negative Prompt</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-24"
                  placeholder="low quality, blurry, distorted..."
                  value={negativePrompt}
                  onChange={(e) => setNegativePrompt(e.target.value)}
                />
              </div>

              <div className="form-control">
                <label className="label cursor-pointer justify-start gap-4">
                  <input
                    type="checkbox"
                    className="checkbox nsfw-toggle"
                    checked={nsfw}
                    onChange={(e) => setNsfw(e.target.checked)}
                  />
                  <span className="label-text text-lg">Enable NSFW Content</span>
                </label>
              </div>
            </div>
          </div>

          {/* Generation Parameters */}
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">Parameters</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Steps</span>
                    <span className="label-text-alt">{steps}</span>
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="50"
                    value={steps}
                    onChange={(e) => setSteps(parseInt(e.target.value))}
                    className="range range-primary"
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">CFG Scale</span>
                    <span className="label-text-alt">{cfgScale}</span>
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="0.5"
                    value={cfgScale}
                    onChange={(e) => setCfgScale(parseFloat(e.target.value))}
                    className="range range-primary"
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Seed (optional)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="Random"
                    className="input input-bordered"
                    value={seed}
                    onChange={(e) => setSeed(e.target.value)}
                  />
                </div>

                {generationType === 'image' ? (
                  <>
                    <div className="form-control">
                      <label className="label">
                        <span className="label-text">Width</span>
                      </label>
                      <select
                        className="select select-bordered"
                        value={width}
                        onChange={(e) => setWidth(parseInt(e.target.value))}
                      >
                        <option value={512}>512px</option>
                        <option value={768}>768px</option>
                        <option value={1024}>1024px</option>
                      </select>
                    </div>

                    <div className="form-control">
                      <label className="label">
                        <span className="label-text">Height</span>
                      </label>
                      <select
                        className="select select-bordered"
                        value={height}
                        onChange={(e) => setHeight(parseInt(e.target.value))}
                      >
                        <option value={512}>512px</option>
                        <option value={768}>768px</option>
                        <option value={1024}>1024px</option>
                      </select>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="form-control">
                      <label className="label">
                        <span className="label-text">Frames</span>
                        <span className="label-text-alt">{frames}</span>
                      </label>
                      <input
                        type="range"
                        min="8"
                        max="64"
                        value={frames}
                        onChange={(e) => setFrames(parseInt(e.target.value))}
                        className="range range-primary"
                      />
                    </div>

                    <div className="form-control">
                      <label className="label">
                        <span className="label-text">FPS</span>
                        <span className="label-text-alt">{fps}</span>
                      </label>
                      <input
                        type="range"
                        min="4"
                        max="30"
                        value={fps}
                        onChange={(e) => setFps(parseInt(e.target.value))}
                        className="range range-primary"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={generating || !selectedAvatar || !prompt.trim()}
              className="btn btn-primary btn-lg px-12"
            >
              {generating ? (
                <>
                  <span className="loading loading-spinner"></span>
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 mr-2" />
                  Generate {generationType === 'image' ? 'Image' : 'Video'}
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default GeneratePage;