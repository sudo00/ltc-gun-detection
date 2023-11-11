export const UploadFile = ({ fetchFile }) => {
    const handleChange = (event) => {
        const formData = new FormData();
        formData.append('UploadForm[video]', event.target.files[0]);
        fetchFile(formData)
    }

    return (
        <div className='uploadFile'>
            <label class="input-file">
                <input type='file' onChange={handleChange} accept='.mp4' />
                <span>Выберите файл</span>
            </label>
        </div>
    )
}
