import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, User, Clock, CheckCircle, XCircle, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { avatarAPI, trainingAPI } from '../services/api';

const AvatarsPage = () => {
  const [avatars, setAvatars] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAvatars();
  }, []);

  const fetchAvatars = async () => {
    try {
      const data = await avatarAPI.list();
      setAvatars(data.avatars || []);
    } catch (error) {
      console.error('Failed to fetch avatars:', error);
      toast.error('Failed to load avatars');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (token) => {
    if (!window.confirm('Are you sure you want to delete this avatar? This action cannot be undone.')) {
      return;
    }

    try {
      await avatarAPI.delete(token);
      toast.success('Avatar deleted successfully');
      fetchAvatars();
    } catch (error) {
      console.error('Failed to delete avatar:', error);
      toast.error('Failed to delete avatar');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'trained':
        return <CheckCircle className="w-5 h-5 text-success" />;
      case 'training':
      case 'preprocessing':
        return <Clock className="w-5 h-5 text-warning animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-error" />;
      default:
        return <Clock className="w-5 h-5 text-info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'trained':
        return 'badge-success';
      case 'training':
      case 'preprocessing':
        return 'badge-warning';
      case 'failed':
        return 'badge-error';
      default:
        return 'badge-info';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">My Avatars</h1>
          <p className="text-lg opacity-70">
            Manage your trained avatar models
          </p>
        </div>
        <Link to="/create-avatar" className="btn btn-primary btn-lg">
          <Plus className="w-5 h-5 mr-2" />
          Create Avatar
        </Link>
      </div>

      {avatars.length === 0 ? (
        <div className="text-center py-16">
          <User className="w-24 h-24 mx-auto mb-6 opacity-30" />
          <h2 className="text-3xl font-bold mb-4">No Avatars Yet</h2>
          <p className="text-lg opacity-70 mb-8">
            Create your first avatar to start generating personalized content
          </p>
          <Link to="/create-avatar" className="btn btn-primary btn-lg">
            <Plus className="w-5 h-5 mr-2" />
            Create Your First Avatar
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {avatars.map((avatar) => (
            <div key={avatar.token} className="card bg-base-200 shadow-xl">
              <div className="card-body">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="avatar placeholder">
                      <div className="bg-neutral-focus text-neutral-content rounded-full w-12">
                        <span className="text-xl">
                          {avatar.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div>
                      <h2 className="card-title text-lg">{avatar.name}</h2>
                      <p className="text-sm opacity-70">{avatar.token}</p>
                    </div>
                  </div>
                  <div className="dropdown dropdown-end">
                    <label tabIndex={0} className="btn btn-ghost btn-sm">
                      ⋮
                    </label>
                    <ul className="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52">
                      {avatar.status === 'trained' && (
                        <li>
                          <Link to={`/generate?avatar=${avatar.token}`}>
                            Generate Content
                          </Link>
                        </li>
                      )}
                      <li>
                        <button
                          onClick={() => handleDelete(avatar.token)}
                          className="text-error"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(avatar.status)}
                    <span className={`badge ${getStatusColor(avatar.status)}`}>
                      {avatar.status.charAt(0).toUpperCase() + avatar.status.slice(1)}
                    </span>
                  </div>

                  {avatar.description && (
                    <p className="text-sm opacity-70">{avatar.description}</p>
                  )}

                  <div className="stats stats-vertical bg-base-300 rounded-lg">
                    <div className="stat py-2">
                      <div className="stat-title text-xs">Training Images</div>
                      <div className="stat-value text-sm">{avatar.training_images_count}</div>
                    </div>
                    <div className="stat py-2">
                      <div className="stat-title text-xs">Created</div>
                      <div className="stat-value text-xs">
                        {new Date(avatar.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card-actions justify-end mt-4">
                  {avatar.status === 'trained' ? (
                    <Link
                      to={`/generate?avatar=${avatar.token}`}
                      className="btn btn-primary btn-sm"
                    >
                      Generate
                    </Link>
                  ) : avatar.status === 'failed' ? (
                    <button className="btn btn-warning btn-sm">
                      Retry Training
                    </button>
                  ) : (
                    <button className="btn btn-ghost btn-sm" disabled>
                      Training...
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AvatarsPage;