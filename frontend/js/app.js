/**
 * app.js — Music Subscription API client
 *
 * To switch backends, change BASE_URL to one of the three constants below.
 */

const EC2_URL    = "http://34.232.160.138";
const ECS_URL    = "http://18.235.243.92";
const LAMBDA_URL = "https://8f7ddpjckd.execute-api.us-east-1.amazonaws.com/prod";

// ↓ Change this to EC2_URL, ECS_URL, or LAMBDA_URL
const BASE_URL = LAMBDA_URL;

const API = (() => {

  /**
   * Core fetch helper.
   * Sends JSON, expects JSON back.
   * Throws on non-2xx responses.
   */
  async function request(method, path, body = null, params = null) {
    let url = BASE_URL + path;

    if (params) {
      const qs = Object.entries(params)
        .filter(([, v]) => v !== "" && v !== null && v !== undefined)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join("&");
      if (qs) url += "?" + qs;
    }

    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw Object.assign(new Error(data.message || "Request failed"), { status: res.status, data });
    }
    return data;
  }

  // ── Auth ─────────────────────────────────────────────────────────────────

  /**
   * POST /login
   * Returns { success: true, user_name } or { success: false, message }
   */
  async function login(email, password) {
    return request("POST", "/login", { email, password });
  }

  /**
   * POST /register
   * Returns { success: true } or { success: false, message }
   */
  async function register(email, user_name, password) {
    return request("POST", "/register", { email, user_name, password });
  }

  // ── Music ─────────────────────────────────────────────────────────────────

  /**
   * GET /music
   * Accepts any combination of { title, artist, year, album } as filters.
   * Returns { songs: [ { title, artist, year, album, image_url }, … ] }
   */
  async function queryMusic({ title = "", artist = "", year = "", album = "" } = {}) {
    return request("GET", "/music", null, { title, artist, year, album });
  }

  // ── Subscriptions ─────────────────────────────────────────────────────────

  /**
   * GET /subscriptions?email=…
   * Returns { subscriptions: [ { title, artist, year, album, image_url }, … ] }
   */
  async function getSubscriptions(email) {
    return request("GET", "/subscriptions", null, { email });
  }

  /**
   * POST /subscriptions
   * Body: { email, title, artist, album, year, image_key }
   * Returns { success: true }
   */
  async function subscribe(email, song) {
    return request("POST", "/subscriptions", { email, ...song });
  }

  /**
   * DELETE /subscriptions
   * Body: { email, title, artist }
   * Returns { success: true }
   */
  async function unsubscribe(email, title, artist) {
    return request("DELETE", "/subscriptions", { email, title, artist });
  }

  return { login, register, queryMusic, getSubscriptions, subscribe, unsubscribe };
})();
