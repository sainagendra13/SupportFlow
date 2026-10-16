
import { useEffect, useState } from "react";
import { Bell, CheckCheck } from "lucide-react";
import { Link } from "react-router-dom";

import api from "../api/client";
import { useAuth } from "../context/AuthContext";


export default function Notifications() {
  const { user } = useAuth();

  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");

  async function loadNotifications() {
    try {
      const response = await api.get("/notifications");

      setNotifications(response.data.notifications);
      setUnreadCount(response.data.unread_count);
      setError("");
    } catch {
      setError("Unable to load notifications");
    }
  }

  useEffect(() => {
    if (!user) return;

    loadNotifications();

    const interval = setInterval(loadNotifications, 30000);

    return () => clearInterval(interval);
  }, [user?.id]);

  async function markRead(notificationId) {
    try {
      await api.patch(`/notifications/${notificationId}/read`);
      await loadNotifications();
    } catch {
      setError("Unable to mark notification as read");
    }
  }

  async function markAllRead() {
    try {
      await api.patch("/notifications/read-all");
      await loadNotifications();
    } catch {
      setError("Unable to mark notifications as read");
    }
  }

  return (
    <div className="notifications-widget">
      <button
        type="button"
        className="notifications-toggle"
        onClick={() => setOpen(!open)}
      >
        <Bell size={19} />
        <span>Notifications</span>

        {unreadCount > 0 && (
          <span className="notifications-count">
            {unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="notifications-panel">
          <div className="notifications-header">
            <strong>Recent notifications</strong>

            {unreadCount > 0 && (
              <button
                type="button"
                onClick={markAllRead}
                title="Mark all as read"
                aria-label="Mark all notifications as read"
              >
                <CheckCheck size={18} />
              </button>
            )}
          </div>

          {error && (
            <p className="notification-error">{error}</p>
          )}

          {notifications.length === 0 ? (
            <p className="notification-empty">
              No notifications yet.
            </p>
          ) : (
            <div className="notifications-list">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${
                    notification.read ? "" : "unread"
                  }`}
                >
                  <Link
                    to={`/tickets/${notification.ticket_id}`}
                    onClick={() => {
                      if (!notification.read) {
                        markRead(notification.id);
                      }
                      setOpen(false);
                    }}
                  >
                    <span>{notification.message}</span>

                    <small>
                      {new Date(
                        notification.created_at
                      ).toLocaleString()}
                    </small>
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
