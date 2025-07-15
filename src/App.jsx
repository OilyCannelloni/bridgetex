

import Editor from "./Editor";
import "ace-builds/src-noconflict/mode-latex";
import "ace-builds/src-noconflict/theme-monokai";
import "ace-builds/src-noconflict/ext-language_tools";

import './App.css'
import ace from "react-ace";


function App() {
  

  return (
    <>
      <div>
          <Editor
          />
      </div>

      
      
    </>
  )
}

export default App
