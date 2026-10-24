import { Route, Routes, Navigate } from 'react-router-dom'
import { Register } from './pages/login-register/Register'
import { Login } from './pages/login-register/Login'
import { StudentHome } from './pages/home/StudentHome'
import { StudentExercises } from './pages/exercises/StudentExercises'

function App() {

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/home-student" element={<StudentHome />} />
      <Route path="/exercises" element={<StudentExercises />} />
    </Routes>
  )
}

export default App
