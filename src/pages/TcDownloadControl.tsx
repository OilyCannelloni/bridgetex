
import { useEffect, useState } from 'react';
import { API_URL } from '../config';
import ProgressBar from '../common/ProgressBar';

interface FileTypes {
    tex: boolean;
    pbn: boolean;
}

interface DownloadTcDTO {
    url: string;
    boards: string;
    file_types: FileTypes;
}

interface TcFileReadyDTO {
    session_id: string;
    file_type: string;
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

interface SiteEvent {
    board_loaded_event: BoardLoadedEvent | null;
    name: string;
    show: boolean;
}


export default function TcDownloadControl() {
    const [lastEvent, setLastEvent] = useState<SiteEvent>({board_loaded_event: null, name: "", show: false})
    const [waiting, setWaiting] = useState(false)
    const [nEvents, setNEvents] = useState(0)


    useEffect(() => {
        if (lastEvent?.name == "click")
            setWaiting(true)
        else 
            setWaiting(false)
    }, [lastEvent])


    const [fileTypes, setFileTypes] = useState({tex: true, pbn: false});

    const handleChange = (e) => {
        const target = e.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        setFileTypes(values => ({...values, [name]: value}))
    }


    var eventSource: EventSource;
    function submit() {
        setLastEvent({...lastEvent, name: "click", show: false})
        const data: DownloadTcDTO = {
            url: (document.getElementById("url-input") as HTMLInputElement)?.value || "",
            boards: (document.getElementById("boards-input") as HTMLInputElement)?.value || "",
            file_types: fileTypes
        };

        if (data.url == "") {
            setLastEvent({board_loaded_event: null, name: "Uzupełnij link do turnieju.", show: true})
            setWaiting(false)
            return
        }

        if (data.file_types.pbn == false && data.file_types.tex == false) {
            setLastEvent({board_loaded_event: null, name: "Wybierz typ pliku.", show: true})
            setWaiting(false)
            return
        }
        
        (async () => {
            const response = await fetch(`${API_URL}/download-tc-init`,
            {
                method: 'POST',
                mode: 'cors',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json'
                },
            })

            const session_id = (await response.json() as SessionIdDTO).session_id;

            eventSource = new EventSource(`${API_URL}/download-tc-sse/${session_id}`);
            eventSource.addEventListener("boardLoaded", (event) => {
                setLastEvent({board_loaded_event: JSON.parse(event.data), name: "", show: true});
                setNEvents(nEvents + 1)
            });

            eventSource.addEventListener("tcFileReady", (event) => {
                let data = JSON.parse(event.data) as TcFileReadyDTO
                console.log(data.file_type)
                const link = document.createElement("a");
                link.href = `${API_URL}/download-file/${session_id}/${data.file_type}`;
                link.download = data.file_type == "tex" ? "analysis.tex" : "board_set.pbn";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                setLastEvent({board_loaded_event: null, name: "Plik wygenerowany pomyślnie.", show: true});
                setNEvents(nEvents + 1)
            });


            eventSource.addEventListener("download_error", (event) => {
                setLastEvent({board_loaded_event: null , name: `Błąd: ${JSON.parse(event.data).message}`, show: true})
                setNEvents(nEvents + 1)
                eventSource.close();
            });

            eventSource.addEventListener("end", () => {
                eventSource.close();
            });
        })()
    }

    return <div className="main">
        <div className="m-10 p-4 bg-stone-500 rounded">
            <div className="m-4 p-4 bg-stone-700 rounded">
                <b>Wklej poniżej link to turnieju</b>, np. https://mzbs.pl/files/2021/wyniki/zs/250820/  
            </div>

            <div className='mx-4'>
                <input type='text' className="p-4 w-full bg-stone-400 border-4 border-stone-800 rounded" id="url-input"></input>
            </div>

            <div className="m-4 mt-8 p-4 bg-stone-700 rounded">
                <b>Numery rozdań</b>, np. 3, 7, 16-21 (opcjonalnie): 
            </div>
            
            <div className="mx-4">
                <input type='text' className="mb-4 p-4 w-full bg-stone-400 border-4 border-stone-800 rounded" id="boards-input" placeholder="Wszystkie">
                </input>
                <div>
                    <span className='mr-2'>Typ:</span> 
                    <span className='ml-2 mr-1'><b>.tex</b></span>
                    <input type='checkbox' name="tex" defaultChecked onChange={handleChange}></input>  
                    <span className='ml-4 mr-1'><b>.pbn</b></span>
                    <input type='checkbox' name="pbn" onChange={handleChange}></input>
                </div>
            </div>

            <div className='mx-4'>
                <div className='my-4'>
                    <button className="bg-green-600 hover:bg-green-500" onClick={submit}>Wyślij</button>
                </div>
            </div>

            <div className='mx-4'>
                <span> 
                    {(() => {
                        if (!lastEvent.show) return ""
                        return lastEvent.board_loaded_event == null
                                ? lastEvent.name
                                : `Przetwarzanie rozdania ${lastEvent.board_loaded_event.sequence_number} z ${lastEvent.board_loaded_event.total_boards}`
                    })()}
                </span>
            </div>
            <div className='px-10'>
                <ProgressBar value={(() => {
                    if (waiting == true)
                        return null;
                    if (lastEvent.board_loaded_event == null) {
                        return 0
                    } else { 
                        return lastEvent.board_loaded_event.sequence_number / lastEvent.board_loaded_event.total_boards * 100
                    }
                })()} />
            </div>
        </div>
    </div>
}

