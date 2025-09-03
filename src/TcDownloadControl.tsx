
import { useEffect, useState } from 'react';
import './TcDownloadControl.css'
import { API_URL } from './config';

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


export default function TcDownloadControl() {
    const [lastEvent, setLastEvent] = useState<BoardLoadedEvent | string>("")
    const [waiting, setWaiting] = useState(false)
    const [clicks, setClicks] = useState(0)
    const [nEvents, setNEvents] = useState(0)

    useEffect(() => {
        setWaiting(true)
    }, [clicks])

    useEffect(() => {
        setWaiting(false)
    }, [nEvents])


    const [fileTypes, setFileTypes] = useState({tex: true, pbn: false});

    const handleChange = (e) => {
        const target = e.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        setFileTypes(values => ({...values, [name]: value}))
    }


    var eventSource: EventSource;
    function submit() {
        setClicks(clicks + 1)
        const data: DownloadTcDTO = {
            url: (document.getElementById("url-input") as HTMLInputElement)?.value || "",
            boards: (document.getElementById("boards-input") as HTMLInputElement)?.value || "",
            file_types: fileTypes
        };

        if (data.url == "") {
            setLastEvent("Uzupełnij link do turnieju.")
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
                setLastEvent(JSON.parse(event.data));
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

                setLastEvent("Plik wygenerowany pomyślnie.");
                setNEvents(nEvents + 1)
            });


            eventSource.addEventListener("download_error", (event) => {
                setLastEvent(`Błąd: ${JSON.parse(event.data).message}`)
                setNEvents(nEvents + 1)
                eventSource.close();
            });

            eventSource.addEventListener("end", () => {
                eventSource.close();
            });
        })()
    }

    return <div className="main">
        <div className="element-box">
            <div className="box-title">
                <b>Wklej poniżej link to turnieju, np.</b> https://mzbs.pl/files/2021/wyniki/zs/250820/  
            </div>
            <div className="box-input-wrapper">
                <input type='text' className="box-input" id="url-input">
                </input>
            </div>

            <div className="box-input-wrapper-blank">
                <div>
                    Numery rozdań, np. 3, 7, 16-21 (opcjonalnie): 
                </div>
                <div className="box-input-wrapper">
                    <input type='text' className="box-input" id="boards-input" placeholder="Wszystkie">
                    </input>
                </div>
                <div>
                    <span className='text-box-sm'>Typ:</span> 
                    <span className='text-box-sm'><b>.tex</b></span>
                    <input type='checkbox' name="tex" defaultChecked onChange={handleChange}></input>  
                    <span className='text-box-sm'><b>.pbn</b></span>
                    <input type='checkbox' name="pbn" onChange={handleChange}></input>
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
                <progress value={(() => {
                    if (waiting == true)
                        return null;

                    if (typeof(lastEvent) == 'string') {
                        return lastEvent
                    } else { 
                        return lastEvent.sequence_number / lastEvent.total_boards
                    }
                })()} />
            </div>
        </div>
        <br/><br/>

        <h2>GPPP</h2>
        <div className='text-div'>Grane są rozdania o numerach pudełek <b>1-30</b> i <b>1-20</b>. Jeśli chcemy wygenerować plik z 5 ostatnimi rozdaniami
            przed przerwą i 5 pierwszymi po przerwie, należy podać numery 26-35, czyli <b>numery sekwencyjne</b>.
        </div>

        <h2>Turnieje etapowe</h2>
        <img width="80%" src='/src/assets/turniej-wieloczesciowy.PNG'></img>
        <div className='text-div'>
        <p>
            Jeśli turniej ma <b>strukturę etapową</b> (obrazek), niemożliwe jest pobranie rozdań ze wszystkich etapów na raz.
            Należy <b>wejść w etap</b> (np. "półfinały") i dopiero teraz skopiować link. Zwróć uwagę na "/X/" na końcu kopiowanego linku
            (strzałka) - to numer etapu.
        </p>
        <p>
            Numery rozdań są sekewncyjne <b>od początku całego turnieju</b>. Oznacza to, że w półfinałach numery to np. 28-54, a w finale 55-90.
        </p>
        </div>

        <h2>3 liga MP</h2>
        
        <img width="80%" src='/src/assets/liga-1.PNG'></img>
        <img width="80%" src='/src/assets/liga-2.PNG'></img>

        <div className='text-div'>
        <p>
            To też <b>jeden duży turniej etapowy</b>. Niepodanie numerów rozdań skończyłoby się pobraniem całego etapu, czyli np. 360 rozdań.
        </p>
        <p>
            Aby pobrać tylko jeden mecz, wchodzimy w pierwsze rozdanie (obrazek 1) i notujemy jego <b>numer sekwencyjny</b> (obrazek 2).
            Następnie podajemy numery rozdań począwszy od tego numeru. W tym przypadku, dla meczu 24-rozdaniowego: <b>301-324</b>
        </p>
        </div>
        
        <h2>
            Ligi centralne
        </h2>
        <div className='text-div'>
            Niestety, program jeszcze nie obsługuje lig centralnych, gdyż nie są one liczone w TC.
        </div>

    </div>
}

