
import { useState, useRef } from "react";
import Editor from "./Editor";
import PdfViewer from "./PdfViewer";


export default function EditorControl() {
    const editorRef = useRef(null);
    const [pdf, setPdf] = useState(null);

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
            "http://multi2diamonds.com:6969/compile-lualatex",
            {
                method: 'POST',
                mode: 'cors',
                body: JSON.stringify({code: code}),
                headers: {
                    'Content-Type': 'application/json'
                },
            }
        )
        .then(resp => resp.blob())
        .then(blob => {
            setPdf(blob)
        })})();
    }


    return <div>
        <div class="code-pdf-container">
            <div style={{float: "left", "width": "50%"}}>
                <div style={{margin: "10px"}}>
                    <Editor editorRef={editorRef}/>
                </div>                
            </div>
            <div style={{float: "left", "width": "50%"}}>
                <div style={{margin: "10px"}}>
                    <PdfViewer blob={pdf}/>
                </div>
            </div>
        </div>
        
        <div class="control-buttons-wrapper">
            <button class="submit-button" onClick={submitCode}>Submit</button>
        </div>
    </div>
}

