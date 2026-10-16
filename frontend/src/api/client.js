
import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 15000,
  withCredentials: true,
  xsrfCookieName: "csrf_token",
  xsrfHeaderName: "X-CSRF-Token",
  withXSRFToken: true,
});

export default api;