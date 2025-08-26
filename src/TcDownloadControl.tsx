
import { useState } from 'react';
import './TcDownloadCOntrol.css'

interface DownloadTcDTO {
    url: string;
    boards: number[];
}

interface SessionIdDTO {
    session_id: string;
}

interface BoardLoadedEvent {
    sequence_number: number;
    board_number: string;
    total_boards: number;
    board_content: string;
}

export default function TcDownloadControl() {
    const [lastEvent, setLastEvent] = useState(null)

    function download_file(session_id: string) {
        
    }

    function submit() {
        const data: DownloadTcDTO = {
            url: (document.getElementById("url-input") as HTMLInputElement)?.value || "",
            boards: [1, 2, 3]
        };
        
        (async () => {
            const response = await fetch(
            "http://localhost:6969/download-tc-init",
            {
                method: 'POST',
                mode: 'cors',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json'
                },
            })

            const session_id = (await response.json() as SessionIdDTO).session_id;

            const eventSource = new EventSource(`http://localhost:6969/download-tc-sse/${session_id}`);
            eventSource.addEventListener("boardLoaded", (event) => {
                console.log("Board loaded:", event.data);
                setLastEvent(event.data);
            });

            eventSource.addEventListener("tcFileReady", (event) => {
                console.log("TC file ready:", event.data);
                download_file(session_id);
            });

            eventSource.onerror = (err) => {
                console.log("SSE error:", err);
                eventSource.close();
            };
        })()
    }


    return <div>
        <div className="url-box">
            <div className="box-title">
                Wklej poniżej link to turnieju, np <br /> https://mzbs.pl/files/2021/wyniki/zs/250820/  
            </div>
            <div className="box-input-wrapper">
                <input type='text' className="box-input" id="url-input">

                </input>
            </div>
        </div>
        
        <div className="control-buttons-wrapper">
            <button className="submit-button" onClick={submit}>Submit</button>
        </div>
    </div>
}

