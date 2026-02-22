import React, { useState } from 'react';
import { useStore } from '../store';
import { Video, Image as ImageIcon, Trash2, Move, Wand2 } from 'lucide-react';
import PexelsModal from './PexelsModal';

const SceneCard = ({ scene, index }) => {
  const { updateScene, removeScene } = useStore();
  const [isPexelsOpen, setIsPexelsOpen] = useState(false);

  const handleMediaSelect = (url, thumbnail) => {
    updateScene(scene.id, { 
      media_type: 'pexels', 
      media_url: url, 
      media_thumbnail: thumbnail 
    });
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 flex gap-4 group hover:border-blue-500/50 transition-colors">
      {/* Index & Drag Handle */}
      <div className="flex flex-col items-center gap-2 pt-2 text-gray-500">
        <span className="font-mono text-sm">#{index + 1}</span>
        <Move size={16} className="cursor-grab hover:text-white" />
        <button 
          onClick={() => removeScene(scene.id)}
          className="mt-auto text-red-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 space-y-3">
        {/* Script Input */}
        <div>
          <label className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1 block">
            Script / Narration
          </label>
          <textarea
            value={scene.text}
            onChange={(e) => updateScene(scene.id, { text: e.target.value })}
            placeholder="Type what the voice should say here..."
            className="w-full bg-gray-900 text-white rounded-lg p-3 border border-gray-700 focus:border-blue-500 outline-none min-h-[80px] resize-none"
          />
        </div>

        {/* Media & Transition Controls */}
        <div className="flex gap-4 items-center">
          
          {/* Visual Selector */}
          <div className="flex-1">
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1 block">
              Visuals
            </label>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => updateScene(scene.id, { media_type: 'gameplay', media_url: null, media_thumbnail: null })}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border ${scene.media_type === 'gameplay' ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-gray-900 border-gray-700 text-gray-400 hover:bg-gray-800'}`}
              >
                <Video size={16} />
                <span className="text-sm">Gameplay</span>
              </button>
              
              <button 
                onClick={() => setIsPexelsOpen(true)}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border ${scene.media_type === 'pexels' ? 'bg-purple-600/20 border-purple-500 text-purple-400' : 'bg-gray-900 border-gray-700 text-gray-400 hover:bg-gray-800'}`}
              >
                {scene.media_thumbnail ? (
                  <img src={scene.media_thumbnail} alt="Selected" className="w-6 h-6 rounded object-cover" />
                ) : (
                  <ImageIcon size={16} />
                )}
                <span className="text-sm truncate max-w-[100px]">{scene.media_type === 'pexels' && scene.media_url ? 'Selected' : 'Search Pexels'}</span>
              </button>
            </div>
          </div>

          {/* Transition */}
          <div className="w-32">
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1 block">
              Transition IN
            </label>
            <select 
              value={scene.transition}
              onChange={(e) => updateScene(scene.id, { transition: e.target.value })}
              className="w-full bg-gray-900 text-white rounded-lg px-3 py-2 border border-gray-700 outline-none text-sm"
            >
              <option value="none">None</option>
              <option value="fade">Crossfade</option>
              <option value="glitch">Glitch</option>
              <option value="zoom_in">Zoom In</option>
              <option value="whip_pan">Whip Pan</option>
              <option value="fade_black">Fade Black</option>
              <option value="flash_white">Flash White</option>
            </select>
          </div>

          {/* Effect (Ken Burns & Viral) */}
          <div className="w-32">
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1 block">
              Effect
            </label>
            <select 
              value={scene.effect}
              onChange={(e) => updateScene(scene.id, { effect: e.target.value })}
              className="w-full bg-gray-900 text-white rounded-lg px-3 py-2 border border-gray-700 outline-none text-sm"
            >
              <option value="none">None</option>
              <option value="zoom_in">Ken Burns (Zoom In)</option>
              <option value="zoom_slam">Zoom Slam (Viral)</option>
              <option value="whip_pan">Whip Pan (Viral)</option>
              <option value="rgb_split">RGB Split (Glitch)</option>
              <option value="vignette">Vignette (Horror)</option>
              <option value="film_grain">Film Grain</option>
            </select>
          </div>
        </div>
      </div>

      <PexelsModal 
        isOpen={isPexelsOpen} 
        onClose={() => setIsPexelsOpen(false)} 
        onSelect={handleMediaSelect}
      />
    </div>
  );
};

export default SceneCard;
