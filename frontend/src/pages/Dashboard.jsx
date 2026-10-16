
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, RefreshCw } from "lucide-react";

import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import StatCard from "../components/StatCard";
import TicketTable from "../components/TicketTable";

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();

  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState({});
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);

    try {
      const [ticketResponse, statsResponse] = await Promise.all([
        api.get("/tickets", {
          params: {
            status: status || undefined,
            priority: priority || undefined,
            limit: 100,
          },
        }),
        api.get("/dashboard/stats"),
      ]);

      setTickets(ticketResponse.data);
      setStats(statsResponse.data);
      setError("");
    } catch (err) {
      if (err.response?.status === 401) {
        await refreshUser();
        navigate("/login", { replace: true });
      } else {
        setError("Unable to load support tickets.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [status, priority]);

 async function updateTicket(ticketId, changes) {
  try {
    await api.patch(`/tickets/${ticketId}`, changes);
    await loadData();
  } catch (err) {
    setError(
      typeof err.response?.data?.detail === "string"
        ? err.response.data.detail
        : "Unable to update ticket."
    );
  }
}

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">WORKSPACE OVERVIEW</p>
          <h1>Dashboard</h1>
          <p className="muted">
            Welcome back, {user?.name || "User"}!
          </p>
        </div>
      {user?.role === "customer" && (
  <Link className="primary-button link-button" to="/tickets/new">
    <Plus size={18} />
    New Ticket
  </Link>
)}

      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Tickets"
          value={stats.total ?? 0}
          color="blue"
        />
        <StatCard
          title="Open"
          value={stats.open ?? 0}
          color="orange"
        />
        <StatCard
          title="In Progress"
          value={stats.in_progress ?? 0}
          color="purple"
        />
        <StatCard
          title="Resolved"
          value={stats.resolved ?? 0}
          color="green"
        />
      </div>

      <section className="content-card">
        <div className="card-heading">
          <div>
            <h2>Support Tickets</h2>
            <p className="muted">
              View and manage support requests
            </p>
          </div>

          <div className="filters">
            <select
              aria-label="Filter by status"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>

            <select
              aria-label="Filter by priority"
              value={priority}
              onChange={(event) => setPriority(event.target.value)}
            >
              <option value="">All priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>

            <button
              className="secondary-button"
              onClick={loadData}
              disabled={loading}
              aria-label="Refresh tickets"
            >
              <RefreshCw size={17} />
            </button>
          </div>
        </div>

        {error && <p className="error-message">{error}</p>}

        {loading ? (
          <p className="loading-message">Loading tickets...</p>
        ) : (
        <TicketTable
          tickets={tickets}
          user={user}
          onTicketUpdate={updateTicket}
        />
        )}
      </section>
    </div>
  );
}
