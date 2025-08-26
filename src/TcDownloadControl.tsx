
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
    const [lastEvent, setLastEvent] = useState<BoardLoadedEvent | string>("")

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
                setLastEvent(JSON.parse(event.data));
            });

            eventSource.addEventListener("tcFileReady", (event) => {
                window.open(`http://localhost:6969/download-tc-file/${session_id}`, "_blank")
            });

            eventSource.addEventListener("download_error", (event) => {
                setLastEvent(`Błąd: ${JSON.parse(event.data).message}`)
                eventSource.close();
            });
        })()
    }

    function renderDescription() {
        return 
    }

    return <div>
        <div className="element-box">
            <div className="box-title">
                Wklej poniżej link to turnieju, np <br /> https://mzbs.pl/files/2021/wyniki/zs/250820/  
            </div>
            <div className="box-input-wrapper">
                <input type='text' className="box-input" id="url-input">
                </input>
            </div>
        </div>
        
        <div className="element-box">
            <div>
                <button className="submit-button" onClick={submit}>Wyślij</button>
            </div>
            <div>
                <span> 
                    {(() => {
                        return typeof(lastEvent) == 'string' 
                                ? lastEvent 
                                : `Processing board ${lastEvent.sequence_number} of ${lastEvent.total_boards}`
                    })()}
                </span>
            </div>
            <div>
                <progress value={typeof(lastEvent) == 'string' 
                                    ? 0
                                    : lastEvent.sequence_number / lastEvent.total_boards} />
            </div>
        </div>
    </div>
}

