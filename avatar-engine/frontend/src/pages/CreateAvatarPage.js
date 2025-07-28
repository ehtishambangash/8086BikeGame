import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, X, User, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { avatarAPI } from '../services/api';

const CreateAvatarPage = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9)
    }));
    
    setFiles(prev => [...prev, ...newFiles].slice(0, 20)); // Max 20 files
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 20
  });

  const removeFile = (id) => {
    setFiles(prev => {
      const updated = prev.filter(f => f.id !== id);
      // Clean up preview URLs
      const removed = prev.find(f => f.id === id);
      if (removed) {
        URL.revokeObjectURL(removed.preview);
      }
      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length < 5) {
      toast.error('Please upload at least 5 images');
      return;
    }
    
    if (!name.trim()) {
      toast.error('Please enter a name for your avatar');
      return;
    }

    setCreating(true);
    
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('description', description);
      
      files.forEach(({ file }) => {
        formData.append('images', file);
      });

      const result = await avatarAPI.create(formData);
      
      toast.success('Avatar creation started! Training will take ~90 minutes.');
      navigate('/avatars');
      
    } catch (error) {
      console.error('Avatar creation failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to create avatar');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Create New Avatar</h1>
        <p className="text-lg opacity-70">
          Upload 5-20 high-quality facial images to train your personalized avatar model
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Avatar Details */}
        <div className="card bg-base-200 shadow-xl">
          <div className="card-body">
            <h2 className="card-title text-2xl mb-4">
              <User className="w-6 h-6" />
              Avatar Details
            </h2>
            
            <div className="form-control">
              <label className="label">
                <span className="label-text text-lg">Avatar Name *</span>
              </label>
              <input
                type="text"
                placeholder="e.g., My Avatar"
                className="input input-bordered input-lg"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            
            <div className="form-control">
              <label className="label">
                <span className="label-text text-lg">Description (optional)</span>
              </label>
              <textarea
                className="textarea textarea-bordered h-24"
                placeholder="Describe your avatar..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Image Upload */}
        <div className="card bg-base-200 shadow-xl">
          <div className="card-body">
            <h2 className="card-title text-2xl mb-4">
              <Upload className="w-6 h-6" />
              Upload Images ({files.length}/20)
            </h2>
            
            <div className="alert alert-info mb-4">
              <AlertCircle className="w-5 h-5" />
              <div>
                <div className="font-semibold">Image Requirements:</div>
                <ul className="text-sm mt-1 space-y-1">
                  <li>• 5-20 high-quality facial images</li>
                  <li>• Clear, well-lit photos with the face prominently visible</li>
                  <li>• Various angles and expressions recommended</li>
                  <li>• JPEG, PNG, or WebP format</li>
                </ul>
              </div>
            </div>

            {/* Upload Area */}
            <div
              {...getRootProps()}
              className={`upload-area rounded-lg p-8 text-center cursor-pointer transition-all ${
                isDragActive ? 'drag-active' : ''
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 mx-auto mb-4 opacity-50" />
              {isDragActive ? (
                <p className="text-lg">Drop the images here...</p>
              ) : (
                <div>
                  <p className="text-lg mb-2">Drag & drop images here, or click to select</p>
                  <p className="text-sm opacity-70">Upload up to 20 images</p>
                </div>
              )}
            </div>

            {/* Image Preview Grid */}
            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Uploaded Images</h3>
                <div className="image-grid">
                  {files.map(({ id, preview, file }) => (
                    <div key={id} className="relative group">
                      <img
                        src={preview}
                        alt="Upload preview"
                        className="w-full h-48 object-cover rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={() => removeFile(id)}
                        className="absolute top-2 right-2 btn btn-circle btn-sm btn-error opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-4 h-4" />
                      </button>
                      <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                        {file.name}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={creating || files.length < 5 || !name.trim()}
            className="btn btn-primary btn-lg px-12"
          >
            {creating ? (
              <>
                <span className="loading loading-spinner"></span>
                Creating Avatar...
              </>
            ) : (
              <>
                <User className="w-5 h-5 mr-2" />
                Create Avatar
              </>
            )}
          </button>
        </div>
      </form>

      {/* Training Info */}
      <div className="card bg-base-200 shadow-xl mt-8">
        <div className="card-body">
          <h2 className="card-title text-2xl mb-4">What Happens Next?</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-bold">
                1
              </div>
              <div>
                <h3 className="font-semibold">Image Preprocessing</h3>
                <p className="text-sm opacity-70">Your images will be processed and optimized for training</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center text-white font-bold">
                2
              </div>
              <div>
                <h3 className="font-semibold">DreamBooth Training</h3>
                <p className="text-sm opacity-70">A personalized LoRA model will be trained (~90 minutes)</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center text-white font-bold">
                3
              </div>
              <div>
                <h3 className="font-semibold">Ready to Generate</h3>
                <p className="text-sm opacity-70">Once complete, you can generate images and videos with your avatar</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateAvatarPage;