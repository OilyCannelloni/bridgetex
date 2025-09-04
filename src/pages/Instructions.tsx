
export default function Instructions() {
  return <div>
            <h2 className="text-2xl font-bold mb-4 mt-6">GPPP</h2>

            <div className='text-left'>Grane są rozdania o numerach pudełek <b>1-30</b> i <b>1-20</b>. Jeśli chcemy wygenerować plik z 5 ostatnimi rozdaniami
                przed przerwą i 5 pierwszymi po przerwie, należy podać numery 26-35, czyli <b>numery sekwencyjne</b>.
            </div>

            <h2 className="text-2xl font-bold mb-4 mt-10">Turnieje etapowe</h2>
            <img width="80%" src='/turniej-wieloczesciowy.png' className="mx-auto m-6"></img>
            <div className='text-left'>
            <p>
                Jeśli turniej ma <b>strukturę etapową</b> (obrazek), niemożliwe jest pobranie rozdań ze wszystkich etapów na raz.
                Należy <b>wejść w etap</b> (np. "półfinały") i dopiero teraz skopiować link. Zwróć uwagę na "/X/" na końcu kopiowanego linku
                (strzałka) - to numer etapu.
            </p>
            <p>
                Numery rozdań są sekewncyjne <b>od początku całego turnieju</b>. Oznacza to, że w półfinałach numery to np. 28-54, a w finale 55-90.
            </p>
            </div>

            <h2 className="text-2xl font-bold mb-4 mt-10">3 liga MP</h2>
            
            <img width="80%" src='/liga-1.png'  className="mx-auto m-6"></img>
            <img width="80%" src='/liga-2.png'  className="mx-auto m-6"></img>

            <div className='text-left'>
            <p>
                To też <b>jeden duży turniej etapowy</b>. Niepodanie numerów rozdań skończyłoby się pobraniem całego etapu, czyli np. 360 rozdań.
            </p>
            <p>
                Aby pobrać tylko jeden mecz, wchodzimy w pierwsze rozdanie (obrazek 1) i notujemy jego <b>numer sekwencyjny</b> (obrazek 2).
                Następnie podajemy numery rozdań począwszy od tego numeru. W tym przypadku, dla meczu 24-rozdaniowego: <b>301-324</b>
            </p>
            </div>
            
            <h2 className="text-2xl font-bold mb-4 mt-10">
                Ligi centralne
            </h2>
            <div className='text-left'>
                <p>Niestety, program jeszcze nie obsługuje lig centralnych, gdyż nie są one liczone w TC.</p>
                <p>Trzeba poprosić sędziego o plik PBN z rozdaniami, a następnie użyć zakładki 'Analiza z PBN'.</p>
            </div>
            <br/><br/><br/><br/><br/>
        </div>
}
