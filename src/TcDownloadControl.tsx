
import { useState } from 'react';
import './TcDownloadCOntrol.css'

interface DownloadTcDTO {
    url: string;
    boards: string;
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

    var eventSource: EventSource;

    function submit() {
        const data: DownloadTcDTO = {
            url: (document.getElementById("url-input") as HTMLInputElement)?.value || "",
            boards: (document.getElementById("boards-input") as HTMLInputElement)?.value || "",
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

            eventSource = new EventSource(`http://localhost:6969/download-tc-sse/${session_id}`);
            eventSource.addEventListener("boardLoaded", (event) => {
                setLastEvent(JSON.parse(event.data));
            });

            eventSource.addEventListener("tcFileReady", (event) => {
                const link = document.createElement("a");
                link.href = `http://localhost:6969/download-tc-file/${session_id}`;
                link.download = "analysis.tex";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                setLastEvent("Plik wygenerowany pomyślnie.");
                eventSource.close();
            });

            eventSource.addEventListener("download_error", (event) => {
                setLastEvent(`Błąd: ${JSON.parse(event.data).message}`)
            });

            eventSource.addEventListener("end", () => {
                eventSource.close();
            });
        })()
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

            <div className="box-input-wrapper-blank">
                <div>
                    Numery rozdań: 
                </div>
                <div className="box-input-wrapper">
                    <input type='text' className="box-input" id="boards-input">
                    </input>
                </div>
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
                                : `Przetwarzanie rozdania ${lastEvent.sequence_number} z ${lastEvent.total_boards}`
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

