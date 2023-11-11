import axios from "axios";
import { useState, useEffect } from "react"
import { UploadFile } from "../components/uploadFile";
import placeHolder from "../images/placeHolder.png"

export const VideoEventsPage = () => {
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([])
    const [selectedImg, setSelectedImg] = useState(placeHolder);

    const [directoryId, setDirectoryId] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            const response = await axios.get('http://92.53.64.152:3000/detection-source/get?id=' + directoryId, {
                headers: {
                    "Content-Type": "multipart/form-data",
                }
            });
            
            const dataset = response.data
            // sort your data in descending order
//            dataset.sort(function(a, b) {
//                return parseInt(b.id) - parseInt(a.id);
//            });  

            setItems(dataset);
            console.log('Fetching data from the server')
        }


        const timer = setInterval(() => {
            if (isLoaded) {
                fetchData();
            }
        }, 1000);
        return () => clearInterval(timer);
    }, [isLoaded]);

    async function fetchPictures(formData) {
        try {
            const response = await axios.post('http://92.53.64.152:3000/detection-source/file', formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                }
            });

            // const response = await axios.get('http://46.146.228.124/detection-source/get?id=1', formData, {
            //     headers: {
            //         "Content-Type": "multipart/form-data",
            //     }
            // });
            console.log(response);

            setDirectoryId(response.data.id);
            console.log(directoryId)
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
                {'' !== directoryId ? <img className='imageStream' src={"http://92.53.64.152:3000/video_feed?id=" + directoryId} /> : <img className='selectedPicture' src={selectedImg} />}
                <UploadFile fetchFile={fetchPictures}></UploadFile>
                <button className='loadingBtn'
                    onClick={() => { setIsLoaded(!isLoaded) }}>
                    {isLoaded ? 'Прекратить подгрузку новых кадров' : 'Продолжить подгрузку новых кадров'}

                </button>
            </div>
            {items.length ? <ul className="pictureFeed">
                {items.map(item => <li key={item.id} style={{ listStyleType: 'none' }}> <img onClick={(e) => changeSelectedImg(e.target.src)} className='picture' src={'http://92.53.64.152:3000/' + item.url} /></li>)}
            </ul>

                : <h1 className="text">Ничего не найдено</h1>
            }

        </div >)
}
