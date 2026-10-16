
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Headphones,
  LayoutDashboard,
  PlusCircle,
  LogOut,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { Users } from "lucide-react";
import Notifications from "./Notifications";

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  async function handleLogout() {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch {
      alert("Unable to log out. Please try again.");
    }
  }

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Headphones size={23} />
        </div>
        <span>SupportFlow</span>
      </div>

      <p className="sidebar-label">WORKSPACE</p>

      <nav className="sidebar-nav">
        <Link
          to="/dashboard"
          className={
            location.pathname === "/dashboard" ? "nav-active" : ""
          }
        >
          <LayoutDashboard size={19} />
          Dashboard
        </Link>

              {user?.role === "customer" && (
  <Link to="/tickets/new" className={
            location.pathname === "/tickets/new" ? "nav-active" : ""
          }>
    <PlusCircle size={19} />
    Create Ticket
  </Link>
)}

{user?.role === "admin" && (
  <Link
    to="/admin/users"
    className={
      location.pathname === "/admin/users"
        ? "nav-active"
        : ""
    }
  >
    <Users size={19} />
    User Management
  </Link>
)}

      </nav>

      <Notifications />
      <div className="sidebar-bottom">
        <div className="sidebar-user">
          <div className="avatar">
            {user?.name?.charAt(0).toUpperCase() || "U"}
          </div>
          <div>
            <strong>{user?.name}</strong>
            <small>{user?.role}</small>
          </div>
        </div>

        <button className="logout-button" onClick={handleLogout}>
          <LogOut size={19} />
          Logout
        </button>
      </div>
    </aside>
  );
}
