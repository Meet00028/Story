import React, { useState } from 'react';
import { useStore } from '../store';
import SceneCard from './SceneCard';
import { Plus, Wand2, Loader } from 'lucide-react';
import axios from 'axios';

const SceneEditor = () => {
  const { scenes, addScene, reorderScenes } = useStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [showPromptInput, setShowPromptInput] = useState(false);

  const generateStory = async () => {
    if (!prompt) return;
    setIsGenerating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/story/generate', { prompt });
      const newScenes = response.data.map((s, i) => ({
        id: Date.now() + i,
        text: s.text,
        media_type: 'pexels', // Default to pexels for AI stories
        media_url: null, // User still needs to pick, or we could auto-search? Let's leave for user to pick but maybe store keyword
        media_keyword: s.media_keyword, // We can use this to pre-fill search later
        media_thumbnail: null,
        transition: s.transition,
        effect: s.effect
      }));
      reorderScenes(newScenes);
      setShowPromptInput(false);
    } catch (error) {
      console.error("Story generation failed", error);
      alert("Failed to generate story. Check backend logs.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-white">Story Timeline</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">{scenes.length} Scenes</span>
          <button 
            onClick={() => setShowPromptInput(!showPromptInput)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-bold text-sm transition-all"
          >
            <Wand2 size={16} />
            AI Write
          </button>
        </div>
      </div>

      {showPromptInput && (
        <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 mb-6 animate-in fade-in slide-in-from-top-4">
          <label className="text-sm text-gray-400 font-bold mb-2 block">What should the video be about?</label>
          <div className="flex gap-2">
            <input 
              type="text" 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && generateStory()}
              placeholder="e.g. The history of the Roman Empire, 5 fun facts about cats..."
              className="flex-1 bg-gray-900 text-white rounded-lg px-4 py-3 border border-gray-700 outline-none focus:border-purple-500"
            />
            <button 
              onClick={generateStory}
              disabled={isGenerating || !prompt}
              className="px-6 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isGenerating ? <Loader className="animate-spin" size={20} /> : 'Generate'}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {scenes.map((scene, index) => (
          <SceneCard key={scene.id} scene={scene} index={index} />
        ))}
      </div>

      <button 
        onClick={addScene}
        className="w-full py-4 border-2 border-dashed border-gray-700 rounded-xl text-gray-400 hover:border-blue-500 hover:text-blue-500 transition-all flex items-center justify-center gap-2"
      >
        <Plus size={20} />
        Add New Scene
      </button>
      
      <div className="h-20" /> {/* Spacer */}
    </div>
  );
};

export default SceneEditor;
