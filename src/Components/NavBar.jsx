import React, { useState, useEffect } from "react";
import '../Styles/NavBarStyle.css';
import RoundedButton from "./RoundedButton";
import LogOut from "./Logout";

function Navbar() {

    return (
        <div className="custom-navbar">
            <div className="custom-nav-left">
                <ul className="custom-nav-links">
                    <li>
                        <RoundedButton
                            label="Home"
                            style={{ backgroundColor: '#55b2ef', color: 'white' }}
                            onClick={() => scrollToSection('home')}
                        />
                    </li>
                    <li>
                        <RoundedButton
                            label="About"
                            style={{ backgroundColor: '#55b2ef', color: 'white' }}
                            onClick={() => scrollToSection('about')}
                        />
                    </li>
                    <li>
                        <RoundedButton
                            label="Team"
                            style={{ backgroundColor: '#55b2ef', color: 'white' }}
                            onClick={() => scrollToSection('team')}
                        />
                    </li>
                </ul>
            </div>
            <div className="custom-nav-right">
                <ul className="custom-nav-links">
                    <RoundedButton routeLink="/rag" label="X-Ray Analysis" style={{ backgroundColor: '#55b2ef', color: 'white' }} />

                    <RoundedButton routeLink="/login" label="LogIn" style={{ backgroundColor: '#55b2ef', color: 'white' }} />
                    <RoundedButton routeLink="/signUp" label="SignUp" style={{ backgroundColor: '#55b2ef', color: 'black' }} />
                
                </ul>
            </div>
        </div>
    );
}

export default Navbar;
