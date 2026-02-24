import React, { useState } from 'react';
import { useStore } from '../store';
import { Mic, Type, Music, Palette } from 'lucide-react';

const Sidebar = () => {
  const [activeTab, setActiveTab] = useState('voice');
  const { globalSettings, setGlobalSettings, subtitleSettings, setSubtitleSettings } = useStore();

  const tabs = [
    { id: 'voice', icon: Mic, label: 'Voice Lab' },
    { id: 'style', icon: Palette, label: 'Style Studio' },
    { id: 'music', icon: Music, label: 'Music' },
  ];

  return (
    <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col h-full">
      {/* Tabs Header */}
      <div className="flex border-b border-gray-800">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-4 flex flex-col items-center gap-1 text-xs font-medium transition-colors ${
              activeTab === tab.id 
                ? 'text-blue-500 border-b-2 border-blue-500 bg-blue-500/5' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon size={20} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        
        {/* VOICE LAB */}
        {activeTab === 'voice' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">AI Narrator</h3>
              <div className="grid grid-cols-1 gap-3">
                {['en-US-ChristopherNeural', 'en-US-AriaNeural', 'en-US-GuyNeural', 'en-US-JennyNeural'].map((voice) => (
                  <button
                    key={voice}
                    onClick={() => setGlobalSettings({ voice })}
                    className={`p-3 rounded-lg border text-left flex items-center justify-between ${
                      globalSettings.voice === voice 
                        ? 'bg-blue-600/20 border-blue-500 text-white' 
                        : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-gray-600'
                    }`}
                  >
                    <span className="text-sm font-medium">{voice.replace('en-US-', '').replace('Neural', '')}</span>
                    {globalSettings.voice === voice && <div className="w-2 h-2 rounded-full bg-blue-500" />}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STYLE STUDIO */}
        {activeTab === 'style' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Subtitle Appearance</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-500 mb-1 block">Font Family</label>
                  <select 
                    value={subtitleSettings.font}
                    onChange={(e) => setSubtitleSettings({ font: e.target.value })}
                    className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 text-sm"
                  >
                    <option value="Arial">Arial</option>
                    <option value="Impact">Impact</option>
                    <option value="Verdana">Verdana</option>
                    <option value="Comic Sans MS">Comic Sans</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Text Color</label>
                    <div className="flex items-center gap-2">
                      <input 
                        type="color" 
                        value={subtitleSettings.color}
                        onChange={(e) => setSubtitleSettings({ color: e.target.value })}
                        className="w-8 h-8 rounded cursor-pointer bg-transparent border-none"
                      />
                      <span className="text-xs text-gray-400">{subtitleSettings.color}</span>
                    </div>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Stroke Color</label>
                    <div className="flex items-center gap-2">
                      <input 
                        type="color" 
                        value={subtitleSettings.strokeColor}
                        onChange={(e) => setSubtitleSettings({ strokeColor: e.target.value })}
                        className="w-8 h-8 rounded cursor-pointer bg-transparent border-none"
                      />
                      <span className="text-xs text-gray-400">{subtitleSettings.strokeColor}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 mb-1 block">Position</label>
                  <div className="flex bg-gray-800 rounded p-1 border border-gray-700">
                    {['top', 'center', 'bottom'].map((pos) => (
                      <button
                        key={pos}
                        onClick={() => setSubtitleSettings({ position: pos })}
                        className={`flex-1 py-1 text-xs rounded capitalize ${
                          subtitleSettings.position === pos 
                            ? 'bg-blue-600 text-white' 
                            : 'text-gray-400 hover:text-white'
                        }`}
                      >
                        {pos}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 mb-1 block">Highlight Style</label>
                  <select 
                    value={subtitleSettings.highlightStyle}
                    onChange={(e) => setSubtitleSettings({ highlightStyle: e.target.value })}
                    className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 text-sm"
                  >
                    <option value="none">None</option>
                    <option value="random">Random Words (Gold)</option>
                    <option value="nouns">Smart Highlight (Green)</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs text-gray-500 mb-1 block">Pop Intensity ({(subtitleSettings.popIntensity || 1.0).toFixed(1)}x)</label>
                  <input 
                    type="range"
                    min="1.0"
                    max="1.5"
                    step="0.1"
                    value={subtitleSettings.popIntensity || 1.0}
                    onChange={(e) => setSubtitleSettings({ popIntensity: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* MUSIC */}
        {activeTab === 'music' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Background Music</h3>
              <div className="p-4 bg-gray-800 rounded-lg border border-gray-700 text-center text-gray-400 text-sm">
                Music selection coming soon...
              </div>
              
              <div className="mt-4">
                <label className="text-xs text-gray-500 mb-1 block">Volume ({Math.round(globalSettings.musicVol * 100)}%)</label>
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.05"
                  value={globalSettings.musicVol}
                  onChange={(e) => setGlobalSettings({ musicVol: parseFloat(e.target.value) })}
                  className="w-full accent-blue-500"
                />
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Sidebar;
