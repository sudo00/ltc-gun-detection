import { Route, Routes } from 'react-router-dom';
import { VideoEventsPage } from './pages/videoEventsPage';
import { NotFoundPage } from './pages/notFoundPage';
import { Header } from './components/Header';

function App() {
  return (
    <div>
      <Header />
      <div className='container'>
        <Routes>
          <Route path='/' element={<VideoEventsPage/>}></Route>
          <Route path='*' element={<NotFoundPage></NotFoundPage>}></Route>
        </Routes >
      </div>
    </div>
  );
}

export default App;
