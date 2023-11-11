import axios from "axios";
import { useState, useEffect } from "react"
import { UploadFile } from "../components/uploadFile";
import placeHolder from "../images/placeHolder.png"
import streamPlaceHolder from "../images/maxresdefault.jpg"

export const VideoEventsPage = () => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([])
    const [selectedImg, setSelectedImg] = useState(placeHolder);
    const [directoryId, setDirectoryId] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            const response = await axios.get('http://ltc-gun-detection.ru:3000/detection-source/get?id=' + directoryId, {
                headers: {
                    "Content-Type": "multipart/form-data",
                }
            });

            const dataset = response.data
            setItems(dataset);
        }


        const timer = setInterval(() => {
            if (isLoaded) {
                fetchData();
            }
        }, 1000);
        return () => clearInterval(timer);
    }, [isLoaded, directoryId]);

    async function fetchPictures(formData) {
        try {
            const response = await axios.post('http://ltc-gun-detection.ru:3000/detection-source/file', formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                }
            });

            setDirectoryId(response.data.id);
            setIsLoaded(true);
        } catch (error) {
            if (error.response) { // get response with a status code not in range 2xx
                console.log(error.response.data);
                console.log(error.response.status);
                console.log(error.response.headers);
            } else if (error.request) { // no response
                console.log(error.request);
            } else { // Something wrong in setting up the request
                console.log('Error', error.message);
            }
            console.log(error.config);
        }
    }

    function changeSelectedImg(string) {
        setSelectedImg(string);
    }

    return (
        <div className="wrapper">

            <div className="content">
                {'' !== directoryId ? <img className='selectedPicture' src={"http://ltc-gun-detection.ru:3000/video_feed?id=" + directoryId} alt="Видео поток" /> : <img className='selectedPicture' src={streamPlaceHolder}  alt="placeholder"/>}
                <UploadFile fetchFile={fetchPictures}></UploadFile>
                <img className="selectedImage" src={selectedImg} alt="placeholder"></img>
            </div>
            {items.length ? <ul className="pictureFeed">
                {items.map(item => <li key={item.id} style={{ listStyleType: 'none' }}> <img onClick={(e) => changeSelectedImg(e.target.src)} className='picture' src={'http://ltc-gun-detection.ru:3000/' + item.url} alt="placeholder" /></li>)}
            </ul>

                : <h1 className="text">Ничего не найдено</h1>
            }
            <div style={{ height: '10vh', width: '100vw' }}>

            </div>
        </div >)
}
