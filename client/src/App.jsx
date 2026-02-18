import React from 'react';
import Sidebar from './components/Sidebar';
import SceneEditor from './components/SceneEditor';
import PreviewPlayer from './components/PreviewPlayer';

function App() {
  return (
    <div className="flex h-screen bg-black text-white overflow-hidden font-sans">
      <Sidebar />
      <SceneEditor />
      <PreviewPlayer />
    </div>
  );
}

export default App;
