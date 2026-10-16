
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../api/client";

export default function NewTicket() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
  });

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await api.post("/tickets", form);
      navigate("/dashboard");
    } catch (err) {
      setError(
        typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : "Unable to create ticket."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="form-container">
      <Link to="/dashboard" className="back-link">
        ← Back to Dashboard
      </Link>

      <section className="content-card">
        <p className="page-eyebrow">NEW REQUEST</p>
        <h1>Create Support Ticket</h1>
        <p className="muted">
          Tell us about the issue so the support team can help.
        </p>

        <form className="ticket-form" onSubmit={handleSubmit}>
          <label htmlFor="title">Ticket title</label>
          <input
            id="title"
            name="title"
            value={form.title}
            onChange={updateField}
            minLength={5}
            maxLength={150}
            placeholder="Example: Cannot access my account"
            required
          />

          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={updateField}
            minLength={10}
            maxLength={5000}
            rows={6}
            placeholder="Describe the problem..."
            required
          />

          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            name="priority"
            value={form.priority}
            onChange={updateField}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>

          {error && <p className="error-message">{error}</p>}

          <button
            className="primary-button"
            disabled={saving}
          >
            {saving ? "Creating..." : "Create Ticket"}
          </button>
        </form>
      </section>
    </div>
  );
}
