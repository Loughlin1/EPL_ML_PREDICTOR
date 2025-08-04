const Footer = () => {
    return (
        <footer className='footer bg-white-200 text-xl font-bold mb-2 text-grey-500 pt-20 flex justify-between'>
            <p>Loughlin Davidson &#169; 2025</p>
            <div className="flex gap-5">
                <h3>Where to find Me:</h3>
                <a href="https://www.linkedin.com/in/loughlin-davidson/" target="_blank" className="hover:bg-grey-500">
                    <img src="/assets/icons/linkedin_icon.png" alt="LinkedIn" className="object-cover size-12" id="linkedin"/>
                </a>
                <a href="https://github.com/Loughlin1?tab=repositories" target="_blank" className="hover:bg-grey-500">
                    <img src="/assets/icons/github_icon.png" alt="GitHub" className="object-cover size-12" id="github" />
                </a>
            </div>
        </footer>
    );
}

export default Footer;