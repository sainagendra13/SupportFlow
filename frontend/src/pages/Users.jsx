
import { useEffect, useState } from "react";
import api from "../api/client";


export default function Users() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [error, setError] = useState("");

  const limit = 50;

  async function loadUsers() {
    setLoading(true);

    try {
      const response = await api.get("/admin/users", {
        params: { skip, limit },
      });

      setUsers(response.data.users);
      setTotal(response.data.total);
      setError("");
    } catch {
      setError("Unable to load users.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUsers();
  }, [skip]);

  async function changeRole(userId, newRole) {
    setUpdatingId(userId);
    setError("");

    try {
      const response = await api.patch(
        `/admin/users/${userId}/role`,
        { role: newRole }
      );

      setUsers((previous) =>
        previous.map((user) =>
          user.id === userId ? response.data : user
        )
      );
    } catch {
      setError("Unable to update user role.");
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">ADMINISTRATION</p>
          <h1>User Management</h1>
          <p className="muted">
            {total} registered users
          </p>
        </div>
      </div>

      <section className="content-card">
        <h2>All Users</h2>
        <p className="muted">
          View accounts and manage customer and agent roles.
        </p>

        {error && (
          <p className="error-message">{error}</p>
        )}

        {loading ? (
          <p className="loading-message">Loading users...</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Current Role</th>
                  <th>Change Role</th>
                </tr>
              </thead>

              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>{user.role}</td>
                    <td>
                      {user.role === "admin" ? (
                        <span>Protected</span>
                      ) : (
                        <select
                          aria-label={`Role for ${user.name}`}
                          value={user.role}
                          disabled={updatingId === user.id}
                          onChange={(event) =>
                            changeRole(
                              user.id,
                              event.target.value
                            )
                          }
                        >
                          <option value="customer">
                            Customer
                          </option>
                          <option value="agent">
                            Agent
                          </option>
                        </select>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="filters" style={{ marginTop: 20 }}>
          <button
            className="secondary-button"
            disabled={skip === 0 || loading}
            onClick={() =>
              setSkip((value) => Math.max(0, value - limit))
            }
          >
            Previous
          </button>

          <span>
            {total === 0 ? 0 : skip + 1}–
            {Math.min(skip + limit, total)} of {total}
          </span>

          <button
            className="secondary-button"
            disabled={skip + limit >= total || loading}
            onClick={() => setSkip((value) => value + limit)}
          >
            Next
          </button>
        </div>
      </section>
    </div>
  );
}
