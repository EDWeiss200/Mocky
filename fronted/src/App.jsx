
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header/Header';
import Body from './components/Body/Body';
import Start from "../src/pages/Start"
import Work from './pages/Work';

const Home = () => (
  <>
    <Header />
    <Body />
  </>
);

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />   
          <Route path="/start" element={<Start />} />  
          <Route path="/work" element={<Work />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App;