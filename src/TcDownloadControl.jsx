
import './TcDownloadCOntrol.css'


export default function TcDownloadControl() {


    function submit() {

    }


    return <div>
        <div class="url-box">
            <div class="box-title">
                Wklej poniżej link to turnieju, np <br /> https://mzbs.pl/files/2021/wyniki/zs/250820/  
            </div>
            <div class="box-input-wrapper">
                <input type='text' class="box-input">

                </input>
            </div>
        </div>
        
        <div class="control-buttons-wrapper">
            <button class="submit-button" onClick={submit}>Submit</button>
        </div>
    </div>
}

