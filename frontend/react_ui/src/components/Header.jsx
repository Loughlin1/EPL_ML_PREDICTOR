
const Header = () => {
  return (
    <header className="bg-white-200 text-3xl font-bold mb-2 text-grey-500 pb-5">
      <nav>
        <ul className="flex gap-10">
          <li><a href="#predictions" className="text-gray-500 hover:text-purple-600">Predictions</a></li>
          <li><a href="#model" className="text-gray-500 hover:text-purple-600">Model Explanation</a></li>
          <li>
            <a href="https://github.com/Loughlin1/EPL_ML_PREDICTOR/tree/main" target="_blank" 
                className="text-gray-500 rounded hover:bg-gray-3 flex gap-1">
              <img src="/assets/icons/github_icon.png" alt="LinkedIn" className="object-cover size-9" id="linkedin"/>
              <p></p>GitHub Link
            </a>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;