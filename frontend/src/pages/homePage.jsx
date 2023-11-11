import React from 'react'
import { useNavigate } from 'react-router-dom'


export function Home() {
    const navigate = useNavigate();
    return (
        <div className='homePage'>
            <h1>
                Здравствуйте, пожалуйста, выберите сценарий для работы с нейросетью
            </h1>
            <ul className='list'>
                <li>
                    <button onClick={() => { navigate('/videoEventsPage') }} className='btn'>Загрузка видео</button>
                </li>
            </ul>
        </div>
    )
}

