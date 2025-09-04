import { Routes, Route, Link } from "react-router-dom";
import Instructions from "./pages/Instructions";
import FromPbn from "./pages/FromPbn";
import TcDownloadControl from "./pages/TcDownloadControl";
import Footer from "./common/Footer";
import LatexEnv from "./pages/LatexEnv";

export default function App() {
  return (
    <div className="flex flex-col min-h-screen items-center max-w-4xl mx-auto px-6">
      {/* Navbar */}
      <div className="w-full sticky top-0 z-50">
        <nav className="bg-gray-800 text-white p-4 flex justify-between items-center w-full">
          {/* Left side: Logo */}
          <Link to="/" className="flex items-center"> 
            <img src="/2diams.png" alt="Logo" className="h-7 mr-2" />
            <span className="font-bold text-lg">Multi2Diamonds</span>
          </Link>

          {/* Right side: Links */}
          <div className="flex gap-8 items-center text-lg ml-10">
            <Link to="/" className="hover:text-amber-400">TeX/PBN z linku TC</Link>
            <Link to="/pbn" className="hover:text-amber-400">TeX z PBN</Link>
            <Link to="/instructions" className="hover:text-amber-400">Instrukcja</Link>
            <Link to="/latex" className="hover:text-amber-400">Środowisko TeX</Link>
          </div>
        </nav>
      </div>

      <main className="flex-1 max-w-4xl mx-auto w-full p-6">
        <Routes>
          <Route path="/" element={<TcDownloadControl />} />
          <Route path="/pbn" element={<FromPbn />} />
          <Route path="/instructions" element={<Instructions />} />
          <Route path="/latex" element={<LatexEnv />} />
        </Routes>
      </main>
        
      {/* Footer always sits at bottom */}
      <Footer />
    </div>
  );
}

