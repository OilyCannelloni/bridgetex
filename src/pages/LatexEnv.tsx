
export default function LatexEnv() {
  return <div>
            <h2 className="text-2xl font-bold mb-4 mt-6">Jak kompilować LaTeX'a?</h2>

            <div className='text-left'>
                1. Zarejestruj się na <a href="https://overleaf.com" target="_blank" className="text-blue-300 hover:text-amber-500">Overleaf</a>.
                Utwórz nowy, pusty projekt.
            </div>

            <div className='text-left'>
                2. Pobierz <a href="https://github.com/OilyCannelloni/macaronibridge/releases/" target="_blank" className="text-blue-300 hover:text-amber-500">
                Pliki BridgeTeX</a> (najnowsze lib.zip), rozpakuj i załaduj folder do projektu.
            </div>

            <div className='text-left'>
                3. W "Menu" w lewym górnym rogu zmień kompilator na "LuaLaTeX"
            </div>

            <div className='text-left'>
                4. Załaduj do projektu wygenerowaną templatkę z rozdaniami i skompiluj ją.
            </div>

            <div className='text-left'>
                5. Udostępnij projekt partnerowi przy użyciu przycisku "Share" i pracujcie nad analizą jednocześnie!
            </div>

            <h2 className="text-2xl font-bold mb-4 mt-6">Nie działa?</h2>

            <div className="text-left">
                Spróbuj <a href="https://github.com/OilyCannelloni/macaronibridge/blob/master/README.md" target="_blank" className="text-blue-300 hover:text-amber-500">
                instrukcję z obrazkami</a> lub <a href="https://www.youtube.com/watch?v=coo9nlIMazs" target="_blank" className="text-blue-300 hover:text-amber-500">
                instrukcję na YouTube</a>.
            </div>
            

            <br/><br/><br/><br/><br/>
        </div>
}
