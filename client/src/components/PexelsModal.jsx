import React, { useState } from 'react';
import axios from 'axios';
import { X, Search, Loader } from 'lucide-react';

const PexelsModal = ({ isOpen, onClose, onSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const searchPexels = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/pexels/search?query=${query}`);
      setResults(response.data.videos || []);
    } catch (error) {
      console.error("Pexels search failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 w-full max-w-4xl rounded-xl border border-gray-700 flex flex-col max-h-[90vh]">
        <div className="p-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="text-xl font-bold text-white">Select Footage</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>
        
        <div className="p-4 flex gap-2">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && searchPexels()}
            placeholder="Search for videos (e.g. 'Ocean', 'City', 'Business')..."
            className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 outline-none border border-gray-700 focus:border-blue-500"
          />
          <button 
            onClick={searchPexels}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2"
          >
            {loading ? <Loader className="animate-spin" size={20} /> : <Search size={20} />}
            Search
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 grid grid-cols-2 md:grid-cols-3 gap-4">
          {results.map((video) => (
            <div 
              key={video.id} 
              className="group relative aspect-[9/16] bg-gray-800 rounded-lg overflow-hidden cursor-pointer border border-transparent hover:border-blue-500"
              onClick={() => {
                const bestFile = video.video_files.find(f => f.height >= 720 && f.height <= 1080) || video.video_files[0];
                onSelect(bestFile.link, video.image);
                onClose();
              }}
            >
              <img src={video.image} alt="Thumbnail" className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white font-bold">Select</span>
              </div>
              <span className="absolute bottom-2 right-2 bg-black/60 text-xs text-white px-2 py-1 rounded">
                {video.duration}s
              </span>
            </div>
          ))}
          {results.length === 0 && !loading && (
            <div className="col-span-full text-center text-gray-500 py-10">
              No results found. Try a different keyword.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PexelsModal;
