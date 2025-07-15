import { useRef } from 'react';
import AceEditor from 'react-ace';

import 'ace-builds/src-noconflict/mode-latex';
import 'ace-builds/src-noconflict/theme-monokai';

export default function MyEditor({ editorRef }) {
  return (
      <AceEditor
        mode="latex"
        theme="monokai"
        name="ace"
        ref={editorRef}
        editorProps={{ $blockScrolling: true }}
        width="100%"
        height="400px"
      />
  );
}


