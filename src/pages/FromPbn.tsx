import { useState } from "react"
import { API_URL } from "../config"
import axios from "axios"


export default function FromPbn() {
    const [file, setFile] = useState<File | null>(null)

    const onFileChange = (event) => {
        setFile(event.target.files[0])
    }

    const onFileUpload = () => {
        if (file == null)
            return
        const formData = new FormData()
        formData.append("pbnFile", file, file.name)
        axios.post(`${API_URL}/pbn-to-tex`, formData)
    }   


    return <div className="m-10 p-4 rounded bg-stone-500">
            <div className="m-4 p-4 rounded bg-stone-700">
                <b>Załaduj plik .pbn, aby wygenerować templatkę LaTeX!</b> 
            </div>
            <div className="m-4 p-4 bg-stone-400 border-4 border-stone-800 rounded">
                <label htmlFor="file-input" >
                    <input type='file' id="file-input" onChange={onFileChange}>
                    </input>
                </label>
            </div>

            <div className="m-4">
                <button className="bg-green-600 hover:bg-green-500" onClick={onFileUpload}>Wyślij</button>
            </div>
        </div>
}
