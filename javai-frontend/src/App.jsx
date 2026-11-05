import { Route, Routes, Navigate } from 'react-router-dom'
import { Register } from './pages/login-register/Register'
import { Login } from './pages/login-register/Login'
import { Home } from './pages/home/Home'
import { Exercise } from './pages/exercises/Exercise'

function App() {

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/home" element={<Home />} />
      <Route path="/exercises" element={<Exercise />} />
    </Routes>
  )
}

export default App
