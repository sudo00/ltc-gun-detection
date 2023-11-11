import React from 'react'
import { Link } from 'react-router-dom'

export function Header() {
    return (
        <nav className='nav'>
            <Link className='site-title link' to={'/'}>Главная страница</Link>
            <ul>
                <li>
                    <Link className='link' to={'/videoEventsPage'}>Загрузить видео</Link>
                </li>

                <li>
                    <Link className='link' to={'/videoEventsPage'}>О нас</Link>
                </li>
            </ul>
        </nav>
    )
}

