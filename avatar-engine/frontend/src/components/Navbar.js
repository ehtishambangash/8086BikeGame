import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { User, Image, Zap, Gallery, Settings } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: User },
    { path: '/avatars', label: 'Avatars', icon: User },
    { path: '/generate', label: 'Generate', icon: Zap },
    { path: '/gallery', label: 'Gallery', icon: Gallery },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar bg-base-200 shadow-lg">
      <div className="container mx-auto">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost normal-case text-xl font-bold">
            <Image className="w-6 h-6 mr-2" />
            Avatar Engine
          </Link>
        </div>
        
        <div className="flex-none">
          <ul className="menu menu-horizontal px-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <li key={path}>
                <Link
                  to={path}
                  className={`btn btn-ghost ${
                    isActive(path) ? 'btn-primary' : ''
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
          
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost btn-circle">
              <Settings className="w-5 h-5" />
            </label>
            <ul className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li><a>Settings</a></li>
              <li><a>About</a></li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;