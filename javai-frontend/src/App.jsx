import { Route, Routes, Navigate } from 'react-router-dom'
import { Register } from './pages/login-register/Register'
import { Login } from './pages/login-register/Login'
import { Home } from './pages/home/Home'
import { Exercise } from './pages/exercises/Exercise'
import { Admin } from './pages/home/Admin'
import { LoadingScreen } from './components/LoadingScreen'
import AuthContext from './context/AuthContext'
import { useContext } from 'react'

function App() {
  const { token, profile, isAdmin } = useContext(AuthContext);

  if (token && !profile?.role) {
    return <LoadingScreen />;
  }

  const defaultAuthRoute = isAdmin ? '/admin' : '/home';

  return (
    <Routes>
      <Route path="/" element={<Navigate to={token ? defaultAuthRoute : "/login"} replace />} />
      <Route path="/login" element={!token ? <Login /> : <Navigate to={defaultAuthRoute} replace />} />
      <Route path="/register" element={!token ? <Register /> : <Navigate to={defaultAuthRoute} replace />} />
      <Route path="/home" element={!token ? <Navigate to="/login" replace /> : isAdmin ? <Navigate to="/admin" replace /> : <Home />} />
      <Route path="/exercises" element={!token ? <Navigate to="/login" replace /> : isAdmin ? <Navigate to="/admin" replace /> : <Exercise />} />
      <Route path="/admin" element={!token ? <Navigate to="/login" replace /> : isAdmin ? <Admin /> : <Navigate to="/home" replace />} />
    </Routes>
  )
}

export default App
