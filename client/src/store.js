import { create } from 'zustand';

export const useStore = create((set) => ({
  globalSettings: {
    voice: "en-US-ChristopherNeural",
    musicVol: 0.1,
    font: "Arial"
  },
  subtitleSettings: {
    font: "Arial",
    fontSize: 60,
    color: "white",
    strokeColor: "black",
    strokeWidth: 2,
    position: "center",
    highlightStyle: "none",
    popIntensity: 1.0
  },
  scenes: [
    {
      id: 1,
      text: "Welcome to the future of video creation.",
      media_type: "gameplay",
      media_url: null,
      media_thumbnail: null,
      transition: "fade",
      effect: "none"
    }
  ],

  setGlobalSettings: (settings) => set((state) => ({
    globalSettings: { ...state.globalSettings, ...settings }
  })),

  setSubtitleSettings: (settings) => set((state) => ({
    subtitleSettings: { ...state.subtitleSettings, ...settings }
  })),

  addScene: () => set((state) => ({
    scenes: [
      ...state.scenes,
      {
        id: Date.now(),
        text: "",
        media_type: "gameplay",
        media_url: null,
        media_thumbnail: null,
        transition: "none",
        effect: "none"
      }
    ]
  })),

  updateScene: (id, updates) => set((state) => ({
    scenes: state.scenes.map((scene) => 
      scene.id === id ? { ...scene, ...updates } : scene
    )
  })),

  removeScene: (id) => set((state) => ({
    scenes: state.scenes.filter((scene) => scene.id !== id)
  })),

  reorderScenes: (newScenes) => set({ scenes: newScenes }),
}));
