
import { Link } from "react-router-dom";

export default function TicketTable({
  tickets,
  user,
  onTicketUpdate,
}) {
  const canManage = ["agent", "admin"].includes(user?.role);

  if (tickets.length === 0) {
    return <p className="empty-message">No tickets found.</p>;
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Ticket</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Created</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td>
                <Link
                  className="ticket-link"
                  to={`/tickets/${ticket.id}`}
                >
                  {ticket.title}
                </Link>
              </td>

              <td>
                {canManage ? (
                  <select
                    value={ticket.priority}
                    onChange={(event) =>
                      onTicketUpdate(ticket.id, {
                        priority: event.target.value,
                      })
                    }
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                ) : (
                  <span className={`priority-badge ${ticket.priority}`}>
                    {ticket.priority}
                  </span>
                )}
              </td>

              <td>
                {canManage ? (
                  <select
                    value={ticket.status}
                    onChange={(event) =>
                      onTicketUpdate(ticket.id, {
                        status: event.target.value,
                      })
                    }
                  >
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                  </select>
                ) : (
                  <span className={`status-badge ${ticket.status}`}>
                    {ticket.status.replace("_", " ")}
                  </span>
                )}
              </td>

              <td>
                {new Date(ticket.created_at).toLocaleDateString()}
              </td>

              <td>
                <Link to={`/tickets/${ticket.id}`}>View</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}