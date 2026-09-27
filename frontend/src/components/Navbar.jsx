import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="nav">
      <div className="container nav-inner">
        <Link to="/" className="nav-brand">
          OrderFlow
        </Link>
        <div className="nav-right">
          {user ? (
            <>
              <span className="nav-user">
                {user.name} ({user.role})
              </span>
              <button className="btn btn-outline btn-sm" onClick={logout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline btn-sm">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
