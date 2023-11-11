import React from 'react'
import { Link } from 'react-router-dom'

export function Header() {
    return (
        <nav className='nav'>
            <Link className='site-title link' to={'/'}>Команда "Чемпионы" 🏆</Link>
            <ul>
                <li>
                    <Link className='link' to={'/videoEventsPage'}>Загрузить видео</Link>
                </li>
            </ul>
        </nav>
    )
}

