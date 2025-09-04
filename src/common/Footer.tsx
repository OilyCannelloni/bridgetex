export default function Footer() {
  return (

    <footer className="bg-gray-800 text-white py-4 mt-8 px-6 w-full">
      <div className="max-w-4xl mx-auto text-center text-gray-400">
        <p>&copy; {new Date().getFullYear()} Bartek Słupik, Krystyna Gasińska.</p>
        <p className="text-sm text-gray-400">
          Błędy proszę zgłaszać na maila b.slupik@gmail.com
        </p>
      </div>
    </footer>
  );
}