# SupportFlow — Customer Support Ticketing System

A full-stack customer support and ticket-management application built using **FastAPI, React, MongoDB, Redis, Celery and Docker**.

SupportFlow allows customers to submit and track support requests, support agents to manage tickets, and administrators to manage users and access privileges. The system includes role-based authorization, asynchronous notifications, dashboard statistics, and containerized deployment.

## Features

### Customer
- Register and log in securely.
- Create support tickets with a title, description and priority.
- View and filter their own tickets.
- Track ticket status: Open, In Progress or Resolved.
- Add comments and communicate with support staff.
- Receive and manage notifications.

### Support Agent
- View customer support tickets.
- Update ticket status and priority.
- Reply to customer comments.
- Receive notifications when tickets or comments are created.
- View overall support-ticket statistics.

### Administrator
- Access all support tickets and agent functionality.
- View registered users with pagination.
- Promote customers to support agents.
- Change agents back to customers.
- Manage tickets and monitor support activity.
- Access user-management features unavailable to customers and agents.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite, React Router, Axios, CSS, Lucide React |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Database | MongoDB, PyMongo Async |
| Authentication | JWT, HttpOnly cookies, Argon2 password hashing |
| Security | Role-Based Access Control, CSRF protection, request-origin validation |
| Caching | Redis |
| Background Processing | Celery with Redis broker |
| Containerization | Docker, Docker Compose, multi-stage Docker builds |
| Reverse Proxy | Nginx |
| CI | GitHub Actions |
| Python Dependencies | uv |

## Architecture

```text
                 Browser
                    |
              React Frontend
                    |
                  Nginx
                    |
             FastAPI REST API
              /     |      \
             /      |       \
        MongoDB    Redis    Celery Queue
           |         |         |
      Persistent   Cache    Celery Worker
        Data                   |
                               |
                            MongoDB
                         Notifications
```

The application uses separate containers for the frontend, FastAPI backend, MongoDB, Redis and Celery worker.

## Authentication and Authorization

SupportFlow uses JWT authentication stored in **HttpOnly cookies**.

After login, the browser automatically includes the authentication cookie with subsequent API requests. React checks the authenticated session using `/api/auth/me`.

Requests that modify protected data also use a signed CSRF token transmitted through an `X-CSRF-Token` header.

Role permissions are enforced by FastAPI dependencies and database queries.

| Operation | Customer | Agent | Admin |
|---|---|---|---|
| Public registration | Yes | No | No |
| Create ticket | Yes | No | No |
| View all tickets | No | Yes | Yes |
| Change ticket status | No | Yes | Yes |
| Change ticket priority | No | Yes | Yes |
| Comment on accessible tickets | Yes | Yes | Yes |
| View all users | No | No | Yes |
| Manage customer/agent roles | No | No | Yes |

Public registration always creates a customer account. Elevated roles cannot be selected during signup.

## Notifications

SupportFlow uses Celery to create asynchronous notifications for ticket events.

- **Ticket created:** Notifies the customer and support staff.
- **Ticket updated:** Notifies the customer when status or priority changes.
- **Customer comment:** Notifies support agents and administrators.
- **Support reply:** Notifies the ticket owner.

Notifications are stored in MongoDB and exposed through authenticated REST endpoints. Users can view recent notifications and mark individual or all notifications as read.

The frontend periodically refreshes notification data.

Celery uses event identifiers and MongoDB upserts to prevent duplicate notifications when tasks are retried.

## Database

MongoDB stores application data in the following collections:

| Collection | Purpose |
|---|---|
| `users` | Account information, hashed passwords and roles |
| `tickets` | Customer support requests |
| `comments` | Ticket conversations |
| `notifications` | User-specific notifications |

The application uses indexes for common user, ticket, comment and notification queries.

A MongoDB collection validator restricts account roles to `customer`, `agent` and `admin`.

## REST API

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register customer |
| POST | `/api/auth/login` | Authenticate and set cookies |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | Log out |

### Tickets

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/tickets` | Create ticket — customer only |
| GET | `/api/tickets` | List accessible tickets |
| GET | `/api/tickets/{ticket_id}` | Retrieve ticket |
| PATCH | `/api/tickets/{ticket_id}` | Update status or priority — staff only |

Ticket listings support filters, sorting and pagination parameters.

### Comments

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/tickets/{ticket_id}/comments` | View ticket comments |
| POST | `/api/tickets/{ticket_id}/comments` | Add comment |

Comments include author information for display in the frontend.

### Notifications

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/notifications` | List current user's notifications |
| PATCH | `/api/notifications/read-all` | Mark all as read |
| PATCH | `/api/notifications/{id}/read` | Mark one as read |

### Administration

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/users` | List registered users |
| PATCH | `/api/admin/users/{user_id}/role` | Change customer/agent role |

### Dashboard and Health

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/dashboard/stats` | Get ticket statistics |
| GET | `/health` | API health check |

## Local Setup

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js and Python are optional when using the complete Docker setup

### 1. Clone the repository

```bash
git clone https://github.com/sainagendra13/SupportFlow.git
cd SupportFlow
```

### 2. Configure environment variables

Create a `.env` file in the project root using `.env.example`.

Generate a JWT secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add the generated secret:

```env
JWT_SECRET=your-generated-secret
```

### 3. Build and start containers

```bash
docker compose up --build -d
```

### 4. Verify services

```bash
docker compose ps
```

### 5. Access the application

| Service | Local URL |
|---|---|
| React application | http://localhost:5173 |
| FastAPI documentation | http://localhost:8000/docs |
| FastAPI health endpoint | http://localhost:8000/health |

### 6. Stop the application

```bash
docker compose down
```

This stops and removes the containers without removing the MongoDB data volume.

## Creating an Administrator for Local Development

For security, public registration cannot create administrator accounts.

To set up an administrator in a local development environment:

1. Register a normal customer account.
2. Open the MongoDB shell:

```bash
docker compose exec mongodb mongosh supportflow
```

3. Promote the intended account:

```javascript
db.users.updateOne(
  { email: "admin@example.com", role: "customer" },
  { $set: { role: "admin" } }
)
```

4. Log in again with that account.

Administrator provisioning on a public deployment should be restricted to the project owner.

## Background Jobs

Celery processes notification tasks independently of the FastAPI request lifecycle.

Supported tasks:

- `ticket_created`
- `ticket_updated`
- `ticket_commented`

View worker logs:

```bash
docker compose logs -f worker
```

## Continuous Integration

The GitHub Actions workflow performs:

- Backend dependency installation with uv.
- Python syntax compilation.
- Frontend dependency installation.
- React production build.
- Backend and frontend Docker image builds.

Automated application tests are not yet included.

## Future Improvements

- Automated API and role-authorization tests.
- Audit logs for status and priority changes.
- Reliable notification delivery using a transactional outbox.
- Server-side pagination enhancements.
- Password reset and account recovery.
- WebSocket or Server-Sent Events notifications.
- Refresh-token rotation and server-side session revocation.
- Monitoring and observability.

## Author

**Sai Nagendra**

GitHub: https://github.com/sainagendra13
Project URL: https://supportflow-frontend-nnkx.onrender.com/

## Project Status

A working portfolio application developed to demonstrate full-stack Python development, REST API design, asynchronous processing, MongoDB integration, authentication, role-based authorization and Docker-based deployment.
