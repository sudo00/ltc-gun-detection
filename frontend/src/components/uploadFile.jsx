import { useState } from 'react'
import { useNavigate } from 'react-router-dom';


export const UploadFile = ({ fetchFile }) => {


    const [selectedFile, setSelectedFile] = useState(null);
    const [uploaded, setUploaded] = useState();

    const handleChange = (event) => {
        console.log(event.target.files);
        // setSelectedFile(event.target.files[0]);
        const formData = new FormData();
        formData.append('UploadForm[video]', event.target.files[0]);
        fetchFile(formData)
    }

    const handleUpload = async () => {
        if (!selectedFile) {
            alert('Вы не выбрали файл');
            return
        }

        const formData = new FormData();
        formData.append('UploadForm[video]', selectedFile);

        fetchFile(formData)
    }


    return (
        <div className='uploadFile'>
            <label class="input-file">
                <input type='file' onChange={handleChange} accept='.mp4' />
                <span>Выберите файл</span>
            </label>
            {/* <button className='inputBtn' onClick={handleUpload}>Загрузить файл</button> */}
        </div>
    )
}
