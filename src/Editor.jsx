import React, { useRef } from 'react';
import AceEditor from 'react-ace';

import 'ace-builds/src-noconflict/mode-latex';
import 'ace-builds/src-noconflict/theme-monokai';

export default function MyEditor() {
  const editorRef = useRef(null);

  const getValue = () => {
    if (editorRef.current) {
      const value = editorRef.current.editor.getValue();
      return value
    }
  };

  function submitCode() {
    const code = getValue();
    console.log(code + "DUPaabaAA");

    (async () => { 
      const response = await fetch(
          "http://localhost:6969/compile-lualatex",
          {
              method: 'POST',
              mode: 'cors',
              body: JSON.stringify({code: code}),
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              },
          }
      )
      const content = await response.json();

      if (!response.ok) {
        console.log(response.status)
      }
      console.log(content)
    })();
    
  }


  return (
    <><div>
      <AceEditor
        mode="latex"
        theme="monokai"
        name="ace"
        ref={editorRef}
        editorProps={{ $blockScrolling: true }}
        width="800px"
        height="600px"
      />
    </div>
    <div class="control-buttons-wrapper">
        <button class="submit-button" onClick={submitCode}>Submit</button>
    </div></>
  );
}


