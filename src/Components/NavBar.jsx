import React, { useState, useEffect } from "react";
import '../Styles/NavBarStyle.css';
import RoundedButton from "./RoundedButton";
import LogOut from "./Logout";

function Navbar() {
    const [logOut, setLogOut] = useState(false);

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('userDetails'));
        if (user) {
            setLogOut(true);
        }
    }, []);

    const scrollToSection = (id) => {
        const section = document.getElementById(id);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <div className="custom-navbar">
            <div className="custom-nav-left">
                <ul className="custom-nav-links">
                    <li>
                        <RoundedButton
                            label="Home"
                            style={{ backgroundColor: '#9bd0f4', color: 'white' }}
                            onClick={() => scrollToSection('home')}
                        />
                    </li>
                    <li>
                        <RoundedButton
                            label="About"
                            style={{ backgroundColor: '#9bd0f4', color: 'white' }}
                            onClick={() => scrollToSection('about')}
                        />
                    </li>
                    <li>
                        <RoundedButton
                            label="Team"
                            style={{ backgroundColor: '#9bd0f4', color: 'white' }}
                            onClick={() => scrollToSection('team')}
                        />
                    </li>
                </ul>
            </div>
            <div className="custom-nav-right">
                <ul className="custom-nav-links">
                    {logOut &&
                        <>
                            <RoundedButton routeLink="/upload" label="PDF Genie" style={{ backgroundColor: '#9bd0f4', color: 'white' }} />
                        </>}
                    {!logOut &&
                        <>
                            <RoundedButton routeLink="/login" label="LogIn" style={{ backgroundColor: '#9bd0f4', color: 'white' }} />
                            <RoundedButton routeLink="/signUp" label="SignUp" style={{ backgroundColor: '#9bd0f4', color: 'black' }} />
                        </>}
                    {logOut && <LogOut />}
                </ul>
            </div>
        </div>
    );
}

export default Navbar;
