import React, { useState, useRef } from 'react';
import { useStore } from '../store';
import axios from 'axios';
import { Play, Loader, Download } from 'lucide-react';

const PreviewPlayer = () => {
  const { scenes, globalSettings, subtitleSettings } = useStore();
  const [videoUrl, setVideoUrl] = useState(null);
  const [isRendering, setIsRendering] = useState(false);
  const videoRef = useRef(null);

  const handleRender = async () => {
    setIsRendering(true);
    try {
      const payload = {
        global_settings: {
          voice: globalSettings.voice,
          music_vol: globalSettings.musicVol
        },
        subtitle_settings: subtitleSettings,
        scenes: scenes.map(s => ({
          text: s.text,
          media_type: s.media_type,
          media_url: s.media_url,
          transition: s.transition,
          effect: s.effect
        }))
      };

      const response = await axios.post('http://localhost:8000/render', payload, {
        responseType: 'blob'
      });

      const url = URL.createObjectURL(new Blob([response.data], { type: 'video/mp4' }));
      setVideoUrl(url);
      if (videoRef.current) {
        videoRef.current.load();
      }
    } catch (error) {
      console.error("Rendering failed", error);
      alert("Rendering failed. Check console for details.");
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <div className="w-[400px] bg-black border-l border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-white font-bold">Preview</h2>
      </div>

      <div className="flex-1 flex flex-col p-6 items-center justify-center bg-gray-900/50">
        <div className="w-full aspect-[9/16] bg-black rounded-xl overflow-hidden shadow-2xl relative border border-gray-800 group">
          {videoUrl ? (
            <video 
              ref={videoRef}
              src={videoUrl} 
              controls 
              className="w-full h-full object-contain"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-gray-600">
              <Play size={48} className="opacity-20" />
            </div>
          )}
          
          {isRendering && (
            <div className="absolute inset-0 bg-black/80 flex flex-col items-center justify-center text-blue-500 z-10">
              <Loader size={48} className="animate-spin mb-4" />
              <span className="font-bold animate-pulse">Rendering...</span>
              <span className="text-xs text-gray-400 mt-2">This may take a minute</span>
            </div>
          )}
        </div>
      </div>

      <div className="p-6 border-t border-gray-800 bg-gray-900">
        <button
          onClick={handleRender}
          disabled={isRendering || scenes.length === 0}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-lg shadow-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isRendering ? (
            <>
              <Loader size={20} className="animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Play size={20} fill="currentColor" />
              Generate Video
            </>
          )}
        </button>
        
        {videoUrl && (
          <a 
            href={videoUrl} 
            download="video.mp4"
            className="mt-3 block text-center text-sm text-gray-400 hover:text-white flex items-center justify-center gap-2"
          >
            <Download size={14} /> Download MP4
          </a>
        )}
      </div>
    </div>
  );
};

export default PreviewPlayer;
