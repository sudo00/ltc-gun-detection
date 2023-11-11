import { Route, Routes, Link } from 'react-router-dom';
import { VideoEventsPage } from './pages/videoEventsPage';
import { NotFoundPage } from './pages/notFoundPage';
import { Home } from './pages/homePage'
import { Header } from './components/Header';

function App() {
  return (
    <div>
      <Header />
      <div className='container'>
        <Routes>
          <Route path='/' element={<Home></Home>}></Route>
          <Route path='/videoEventsPage' element={<VideoEventsPage></VideoEventsPage>}></Route>
          <Route path='*' element={<NotFoundPage></NotFoundPage>}></Route>
        </Routes >
      </div>
    </div>
  );
}

export default App;
