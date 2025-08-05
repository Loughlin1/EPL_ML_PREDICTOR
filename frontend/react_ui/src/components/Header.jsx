import { useState, useEffect } from 'react';

const Header = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen((open) => !open); 
  };

  return (
    <header className="bg-white-200 text-xl md:text-2xl lg:text-3xl font-bold mb-2 text-grey-500 pb-5">
      <nav className="dvs-header">
        <ul className='flex wrap justify-between align-center'>
          <li>
            <a href="#"><img src="/assets/icons/premier_league_icon.png" alt="Logo" className="object-cover size-16 rounded" id="logo" /></a>  
          </li>
          <li class={`dvs-header__menuItems ${isOpen ? "is-open" : ""}`}>
            <ul>
              <li className="align-center gap-4 lg:gap-10 wrap">
                <a href="#predictions" className="text-gray-500 hover:text-purple-600">Predictions</a>
                <a href="#model" className="text-gray-500 hover:text-purple-600">Explanation</a>
                <a href="https://github.com/Loughlin1/EPL_ML_PREDICTOR/tree/main" target="_blank" 
                className="bg-gray-200 text-gray-500 rounded hover:bg-gray-300">
                  <div className='flex items-center gap-2'>
                    <img src="/assets/icons/github_icon.png" alt="LinkedIn" className="object-cover size-9 " id="linkedin"/>
                    <p className=''>GitHub Link</p>
                  </div>
                </a>
              </li>
            </ul>
          </li>
          <li className="dvs-header__trigger" onClick={toggleMenu}>
            <img src="/assets/icons/burger-bar.png" alt="Burger Menu" className='object-cover size-16' />
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;