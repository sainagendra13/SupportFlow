
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../api/client";

export default function TicketDetails() {
  const { id } = useParams();

  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");

  async function loadTicket() {
    try {
      const [ticketResponse, commentResponse] = await Promise.all([
        api.get(`/tickets/${id}`),
        api.get(`/tickets/${id}/comments`),
      ]);

      setTicket(ticketResponse.data);
      setComments(commentResponse.data);
      setError("");
    } catch {
      setError("Ticket not found or access denied.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTicket();
  }, [id]);

  async function handleComment(event) {
    event.preventDefault();
    setPosting(true);
    setError("");

    try {
      await api.post(`/tickets/${id}/comments`, {
        message,
      });

      setMessage("");
      await loadTicket();
    } catch (err) {
      setError(
        typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : "Unable to add comment."
      );
    } finally {
      setPosting(false);
    }
  }

  if (loading) {
    return <p className="loading-message">Loading ticket...</p>;
  }

  if (!ticket) {
    return <p className="error-message">{error}</p>;
  }

  return (
    <div className="form-container">
      <Link to="/dashboard" className="back-link">
        ← Back to Dashboard
      </Link>

      <section className="content-card">
        <div className="detail-header">
          <h1>{ticket.title}</h1>
          <span className={`priority-badge ${ticket.priority}`}>
            {ticket.priority}
          </span>
        </div>

        <span className={`status-badge ${ticket.status}`}>
          {ticket.status.replace("_", " ")}
        </span>

        <p className="ticket-description">
          {ticket.description}
        </p>

        <div className="section-divider" />

        <h2>Comments ({comments.length})</h2>

        <div className="comments-list">
          {comments.map((comment) => (
  <div className="comment-card" key={comment.id}>
    <div className="comment-author">
      <strong>{comment.author_name}</strong>
      <span className={`comment-role ${comment.author_role}`}>
        {comment.author_role}
      </span>
    </div>

    <p>{comment.message}</p>

    <small>
      {new Date(comment.created_at).toLocaleString()}
    </small>
  </div>
))}

          {comments.length === 0 && (
            <p className="muted">No comments yet.</p>
          )}
        </div>

        <form className="ticket-form" onSubmit={handleComment}>
          <label htmlFor="message">Add a comment</label>
          <textarea
            id="message"
            rows={4}
            maxLength={2000}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            required
          />

          {error && <p className="error-message">{error}</p>}

          <button
            className="primary-button"
            disabled={posting}
          >
            {posting ? "Posting..." : "Post Comment"}
          </button>
        </form>
      </section>
    </div>
  );
}
